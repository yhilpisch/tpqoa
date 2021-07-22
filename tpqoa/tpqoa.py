#
# tpqoa is a wrapper class for the
# Oanda v20 API (RESTful & streaming)
# making use of the v20 Python package
#
# (c) Dr. Yves J. Hilpisch
# The Python Quants GmbH
#
#
# Trading forex/CFDs on margin carries a high level of risk and may
# not be suitable for all investors as you could sustain losses
# in excess of deposits. Leverage can work against you. Due to the certain
# restrictions imposed by the local law and regulation, German resident
# retail client(s) could sustain a total loss of deposited funds but are
# not subject to subsequent payment obligations beyond the deposited funds.
# Be aware and fully understand all risks associated with
# the market and trading. Prior to trading any products,
# carefully consider your financial situation and
# experience level. Any opinions, news, research, analyses, prices,
# or other information is provided as general market commentary, and does not
# constitute investment advice. The Python Quants GmbH will not accept
# liability for any loss or damage, including without limitation to,
# any loss of profit, which may arise directly or indirectly from use
# of or reliance on such information.
#
# The tpqoa package is intended as a technological illustration only.
# It comes with no warranties or representations,
# to the extent permitted by applicable law.
#
import _thread
import configparser
import json
import signal
import threading
from time import sleep

import pandas as pd
import v20
from v20.transaction import StopLossDetails, ClientExtensions
from v20.transaction import TrailingStopLossDetails, TakeProfitDetails

MAX_REQUEST_COUNT = float(5000)


class Job(threading.Thread):
    def __init__(self, job_callable, args=None):
        threading.Thread.__init__(self)
        self.callable = job_callable
        self.args = args

        # The shutdown_flag is a threading.Event object that
        # indicates whether the thread should be terminated.
        self.shutdown_flag = threading.Event()
        self.job = None
        self.exception = None

    def run(self):
        print('Thread #%s started' % self.ident)
        try:
            self.job = self.callable
            while not self.shutdown_flag.is_set():
                print("Starting job loop...")
                if self.args is None:
                    self.job()
                else:
                    self.job(self.args)
        except Exception as e:
            import sys
            import traceback
            print(traceback.format_exc())
            self.exception = e
            _thread.interrupt_main()


class ServiceExit(Exception):
    """
    Custom exception which is used to trigger the clean exit
    of all running threads and the main program.
    """

    def __init__(self, message=None):
        self.message = message

    def __repr__(self):
        return repr(self.message)


def service_shutdown(signum, frame):
    print('exiting ...')
    raise ServiceExit


class tpqoa(object):
    ''' tpqoa is a Python wrapper class for the Oanda v20 API. '''

    def __init__(self, conf_file):
        ''' Init function is expecting a configuration file with
        the following content:

        [oanda]
        account_id = XYZ-ABC-...
        access_token = ZYXCAB...
        account_type = practice (default) or live

        Parameters
        ==========
        conf_file: string
            path to and filename of the configuration file,
            e.g. '/home/me/oanda.cfg'
        '''
        self.config = configparser.ConfigParser()
        self.config.read(conf_file)
        self.access_token = self.config['oanda']['access_token']
        self.account_id = self.config['oanda']['account_id']
        self.account_type = self.config['oanda']['account_type']

        if self.account_type == 'live':
            self.hostname = 'api-fxtrade.oanda.com'
            self.stream_hostname = 'stream-fxtrade.oanda.com'
        else:
            self.hostname = 'api-fxpractice.oanda.com'
            self.stream_hostname = 'stream-fxpractice.oanda.com'

        self.ctx = v20.Context(
            hostname=self.hostname,
            port=443,
            token=self.access_token,
            poll_timeout=10
        )
        self.ctx_stream = v20.Context(
            hostname=self.stream_hostname,
            port=443,
            token=self.access_token,
        )

        self.suffix = '.000000000Z'
        self.stop_stream = False

    def get_instruments(self):
        ''' Retrieves and returns all instruments for the given account. '''
        resp = self.ctx.account.instruments(self.account_id)
        instruments = resp.get('instruments')
        instruments = [ins.dict() for ins in instruments]
        instruments = [(ins['displayName'], ins['name'])
                       for ins in instruments]
        return sorted(instruments)

    def get_prices(self, instrument):
        ''' Returns the current BID/ASK prices for instrument. '''
        r = self.ctx.pricing.get(self.account_id, instruments=instrument)
        r = json.loads(r.raw_body)
        bid = float(r['prices'][0]['closeoutBid'])
        ask = float(r['prices'][0]['closeoutAsk'])
        return r['time'], bid, ask

    def transform_datetime(self, dati):
        ''' Transforms Python datetime object to string. '''
        if isinstance(dati, str):
            dati = pd.Timestamp(dati).to_pydatetime()
        return dati.isoformat('T') + self.suffix

    def retrieve_data(self, instrument, start, end, granularity, price):
        raw = self.ctx.instrument.candles(
            instrument=instrument,
            fromTime=start, toTime=end,
            granularity=granularity, price=price)
        raw = raw.get('candles')
        raw = [cs.dict() for cs in raw]
        if price == 'A':
            for cs in raw:
                cs.update(cs['ask'])
                del cs['ask']
        elif price == 'B':
            for cs in raw:
                cs.update(cs['bid'])
                del cs['bid']
        elif price == 'M':
            for cs in raw:
                cs.update(cs['mid'])
                del cs['mid']
        else:
            raise ValueError("price must be either 'B', 'A' or 'M'.")
        if len(raw) == 0:
            return pd.DataFrame()  # return empty DataFrame if no data
        data = pd.DataFrame(raw)
        data['time'] = pd.to_datetime(data['time'])
        data = data.set_index('time')
        data.index = pd.DatetimeIndex(data.index)
        for col in list('ohlc'):
            data[col] = data[col].astype(float)
        return data

    def get_history(self, instrument, start, end,
                    granularity, price, localize=True):
        ''' Retrieves historical data for instrument.

        Parameters
        ==========
        instrument: string
            valid instrument name
        start, end: datetime, str
            Python datetime or string objects for start and end
        granularity: string
            a string like 'S5', 'M1' or 'D'
        price: string
            one of 'A' (ask), 'B' (bid) or 'M' (middle)

        Returns
        =======
        data: pd.DataFrame
            pandas DataFrame object with data
        '''
        if granularity.startswith('S') or granularity.startswith('M') \
            or granularity.startswith('H'):
            multiplier = float("".join(filter(str.isdigit, granularity)))
            if granularity.startswith('S'):
                # freq = '1h'
                freq = f"{int(MAX_REQUEST_COUNT * multiplier / float(3600))}H"
            else:
                # freq = 'D'
                freq = f"{int(MAX_REQUEST_COUNT * multiplier / float(1440))}D"
            data = pd.DataFrame()
            dr = pd.date_range(start, end, freq=freq)

            for t in range(len(dr)):
                batch_start = self.transform_datetime(dr[t])
                if t != len(dr) - 1:
                    batch_end = self.transform_datetime(dr[t + 1])
                else:
                    batch_end = self.transform_datetime(end)

                batch = self.retrieve_data(instrument, batch_start, batch_end,
                                           granularity, price)
                data = data.append(batch)
        else:
            start = self.transform_datetime(start)
            end = self.transform_datetime(end)
            data = self.retrieve_data(instrument, start, end,
                                      granularity, price)
        if localize:
            data.index = data.index.tz_localize(None)

        return data[['o', 'h', 'l', 'c', 'volume', 'complete']]

    def create_order(self, instrument, units, price=None, sl_distance=None,
                     tsl_distance=None, tp_price=None, comment=None,
                     touch=False, suppress=False, ret=False):
        ''' Places order with Oanda.

        Parameters
        ==========
        instrument: string
            valid instrument name
        units: int
            number of units of instrument to be bought
            (positive int, eg 'units=50')
            or to be sold (negative int, eg 'units=-100')
        price: float
            limit order price, touch order price
        sl_distance: float
            stop loss distance price, mandatory eg in Germany
        tsl_distance: float
            trailing stop loss distance
        tp_price: float
            take profit price to be used for the trade
        comment: str
            string
        touch: boolean
            market_if_touched order (requires price to be set)
        suppress: boolean
            whether to suppress print out
        ret: boolean
            whether to return the order object
        '''
        client_ext = ClientExtensions(
            comment=comment) if comment is not None else None
        sl_details = (StopLossDetails(distance=sl_distance,
                                      clientExtensions=client_ext)
                      if sl_distance is not None else None)
        tsl_details = (TrailingStopLossDetails(distance=tsl_distance,
                                               clientExtensions=client_ext)
                       if tsl_distance is not None else None)
        tp_details = (TakeProfitDetails(
            price=tp_price, clientExtensions=client_ext)
            if tp_price is not None else None)
        if price is None:
            request = self.ctx.order.market(
                self.account_id,
                instrument=instrument,
                units=units,
                stopLossOnFill=sl_details,
                trailingStopLossOnFill=tsl_details,
                takeProfitOnFill=tp_details,
            )
        elif touch:
            request = self.ctx.order.market_if_touched(
                self.account_id,
                instrument=instrument,
                price=price,
                units=units,
                stopLossOnFill=sl_details,
                trailingStopLossOnFill=tsl_details,
                takeProfitOnFill=tp_details
            )
        else:
            request = self.ctx.order.limit(
                self.account_id,
                instrument=instrument,
                price=price,
                units=units,
                stopLossOnFill=sl_details,
                trailingStopLossOnFill=tsl_details,
                takeProfitOnFill=tp_details
            )

        # First checking if the order is rejected
        if 'orderRejectTransaction' in request.body:
            order = request.get('orderRejectTransaction')
        elif 'orderFillTransaction' in request.body:
            order = request.get('orderFillTransaction')
        elif 'orderCreateTransaction' in request.body:
            order = request.get('orderCreateTransaction')
        else:
            # This case does not happen.  But keeping this for completeness.
            order = None

        if not suppress and order is not None:
            print('\n\n', order.dict(), '\n')
        if ret is True:
            return order.dict() if order is not None else None

    def stream_data(self, instrument, stop=None, ret=False, callback=None):
        ''' Starts a real-time data stream.

        Parameters
        ==========
        instrument: string
            valid instrument name
        '''
        self.stream_instrument = instrument
        self.ticks = 0
        response = self.ctx_stream.pricing.stream(
            self.account_id, snapshot=True,
            instruments=instrument)
        msgs = []
        for msg_type, msg in response.parts():
            msgs.append(msg)
            # print(msg_type, msg)
            if msg_type == 'pricing.ClientPrice':
                self.ticks += 1
                self.time = msg.time
                if callback is not None:
                    callback(msg.instrument, msg.time,
                             float(msg.bids[0].dict()['price']),
                             float(msg.asks[0].dict()['price']))
                else:
                    self.on_success(msg.time,
                                    float(msg.bids[0].dict()['price']),
                                    float(msg.asks[0].dict()['price']))
                if stop is not None:
                    if self.ticks >= stop:
                        if ret:
                            return msgs
                        break
            if self.stop_stream:
                if ret:
                    return msgs
                break

    def _stream_data_failsafe_thread(self, args):
        try:
            print("Starting price streaming")
            self.stream_data(args[0], callback=args[1])
        except Exception as e:
            import sys
            import traceback
            print(traceback.format_exc())
            sleep(3)
            return

    def stream_data_failsafe(self, instrument, callback=None):
        signal.signal(signal.SIGTERM, service_shutdown)
        signal.signal(signal.SIGINT, service_shutdown)
        signal.signal(signal.SIGSEGV, service_shutdown)
        try:
            price_stream_thread = Job(self._stream_data_failsafe_thread,
                                      [instrument, callback])
            price_stream_thread.start()
            return price_stream_thread
        except ServiceExit as e:
            print('Handling exception')
            import sys
            import traceback
            print(traceback)
            price_stream_thread.shutdown_flag.set()
            price_stream_thread.join()

    def on_success(self, time, bid, ask):
        ''' Method called when new data is retrieved. '''
        print(time, bid, ask)

    def get_account_summary(self, detailed=False):
        ''' Returns summary data for Oanda account.'''
        if detailed is True:
            response = self.ctx.account.get(self.account_id)
        else:
            response = self.ctx.account.summary(self.account_id)
        raw = response.get('account')
        return raw.dict()

    def get_transaction(self, tid=0):
        ''' Retrieves and returns transaction data. '''
        response = self.ctx.transaction.get(self.account_id, tid)
        transaction = response.get('transaction')
        return transaction.dict()

    def get_transactions(self, tid=0):
        ''' Retrieves and returns transactions data. '''
        response = self.ctx.transaction.since(self.account_id, id=tid)
        transactions = response.get('transactions')
        transactions = [t.dict() for t in transactions]
        return transactions

    def print_transactions(self, tid=0):
        ''' Prints basic transactions data. '''
        transactions = self.get_transactions(tid)
        for trans in transactions:
            try:
                templ = '%4s | %s | %7s | %8s | %8s'
                print(templ % (trans['id'],
                               trans['time'][:-8],
                               trans['instrument'],
                               trans['units'],
                               trans['pl']))
            except Exception:
                pass

    def get_positions(self):
        ''' Retrieves and returns positions data. '''
        response = self.ctx.position.list_open(self.account_id).body
        positions = [p.dict() for p in response.get('positions')]
        return positions
