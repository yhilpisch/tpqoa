<img src="http://hilpisch.com/tpq_logo.png" alt="The Python Quants" width="35%" align="right" border="0"><br>

# tpqoa

## Algorithmic Trading with Oanda

`tpqoa` is a wrapper class for the Oanda REST API v20 (http://developer.oanda.com/). It makes use of the Python package `v20` from Oanda (https://github.com/oanda/v20-python). The package is authored and maintained by The Python Quants GmbH. &copy; Dr. Yves J. Hilpisch. MIT License.

## Disclaimer

Trading forex/CFDs on margin carries a high level of risk and may not be suitable for all investors as you could sustain losses in excess of deposits. Leverage can work against you. Due to the certain restrictions imposed by the local law and regulation, German resident retail client(s) could sustain a total loss of deposited funds but are not subject to subsequent payment obligations beyond the deposited funds. Be aware and fully understand all risks associated with the market and trading. Prior to trading any products, carefully consider your financial situation and experience level. Any opinions, news, research, analyses, prices, code examples or other information is provided as general market commentary, and does not constitute investment advice. The Python Quants GmbH will not accept liability for any loss or damage, including without limitation to, any loss of profit, which may arise directly or indirectly from use of or reliance on such information.

The `tpqoa` package is intended as a technological illustration only. It comes with no warranties or representations, to the extent permitted by applicable law.

## Installation

Installing from source via `Git` and `Github`:

    git clone https://github.com/yhilpisch/tpqoa
    cd tpqoa
    python setup.py install
    
Using `pip` in combination with `Github`:

    pip install --upgrade git+https://github.com/yhilpisch/tpqoa.git


## Connection

In order to connect to the API, you need to have at least a practice account with Oanda (https://oanda.com/). Once logged in to you account, you can create an API token and can copy your account number. These are expected to be stored in a configuration file, with name `oanda.cfg`, for instance, as follows:

    [oanda]
    account_id = XYZ-ABC-...
    access_token = ZYXCAB...
    account_type = practice (default) or live

You can then set up an API connection by instantiating a connection object.


```python
import tpqoa
```


```python
oanda = tpqoa.tpqoa('oanda.cfg')
```

## Available Instruments

The `get_instruments()` method retrieves all available instruments.


```python
ins = oanda.get_instruments()
```


```python
ins[:10]
```




    [('AUD/CAD', 'AUD_CAD'),
     ('AUD/CHF', 'AUD_CHF'),
     ('AUD/HKD', 'AUD_HKD'),
     ('AUD/JPY', 'AUD_JPY'),
     ('AUD/NZD', 'AUD_NZD'),
     ('AUD/SGD', 'AUD_SGD'),
     ('AUD/USD', 'AUD_USD'),
     ('Australia 200', 'AU200_AUD'),
     ('Brent Crude Oil', 'BCO_USD'),
     ('Bund', 'DE10YB_EUR')]



## Historical Data

The `get_history()` method retrieves historical data.


```python
help(oanda.get_history)
```

    Help on method get_history in module tpqoa.tpqoa:
    
    get_history(instrument, start, end, granularity, price, localize=True) method of tpqoa.tpqoa.tpqoa instance
        Retrieves historical data for instrument.
        
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
    



```python
data = oanda.get_history(instrument='EUR_USD',
                  start='2020-07-01',
                  end='2021-05-31',
                  granularity='D',
                  price='A')
```


```python
data.info()
```

    <class 'pandas.core.frame.DataFrame'>
    DatetimeIndex: 237 entries, 2020-06-30 21:00:00 to 2021-05-30 21:00:00
    Data columns (total 6 columns):
     #   Column    Non-Null Count  Dtype  
    ---  ------    --------------  -----  
     0   o         237 non-null    float64
     1   h         237 non-null    float64
     2   l         237 non-null    float64
     3   c         237 non-null    float64
     4   volume    237 non-null    int64  
     5   complete  237 non-null    bool   
    dtypes: bool(1), float64(4), int64(1)
    memory usage: 11.3 KB



```python
print(data.head())
```

                               o        h        l        c  volume  complete
    time                                                                     
    2020-06-30 21:00:00  1.12393  1.12758  1.11858  1.12527   90252      True
    2020-07-01 21:00:00  1.12527  1.13033  1.12245  1.12403   90789      True
    2020-07-02 21:00:00  1.12403  1.12555  1.12200  1.12529   59036      True
    2020-07-05 21:00:00  1.12523  1.13462  1.12445  1.13113   81756      True
    2020-07-06 21:00:00  1.13168  1.13333  1.12598  1.12762   92426      True


## Streaming Data

The method `stream_data()` allows the streaming of real-time data (bid & ask).


```python
oanda.stream_data('EUR_USD', stop=3)
```

    2021-06-22T06:47:54.604916136Z 1.19031 1.19043
    2021-06-22T06:47:55.038676749Z 1.19026 1.19039
    2021-06-22T06:47:55.428426626Z 1.19028 1.19039


By redefining the `on_success()` method, you can control what happes with the streaming data.


```python
class myOanda(tpqoa.tpqoa):
    def on_success(self, time, bid, ask):
        ''' Method called when new data is retrieved. '''
        print('BID: {:.5f} | ASK: {:.5f}'.format(bid, ask))
```


```python
my_oanda = myOanda('oanda.cfg')
```


```python
my_oanda.stream_data('EUR_USD', stop=5)
```

    BID: 1.19029 | ASK: 1.19042
    BID: 1.19028 | ASK: 1.19041
    BID: 1.19027 | ASK: 1.19039
    BID: 1.19028 | ASK: 1.19040
    BID: 1.19029 | ASK: 1.19041


## Other Methods

Other major methods are:


```python
help(oanda.create_order)
```

    Help on method create_order in module tpqoa.tpqoa:
    
    create_order(instrument, units, price=None, sl_distance=None, tsl_distance=None, tp_price=None, comment=None, touch=False, suppress=False, ret=False) method of tpqoa.tpqoa.tpqoa instance
        Places order with Oanda.
        
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
    



```python
# going long 100 units
# sl_distance of 20 pips
oanda.create_order('EUR_USD', units=100, sl_distance=0.002)
```

    
    
     {'id': '2736', 'time': '2021-06-22T06:47:57.379175075Z', 'userID': 13834683, 'accountID': '101-004-13834683-001', 'batchID': '2735', 'requestID': '78870588578569727', 'type': 'ORDER_FILL', 'orderID': '2735', 'instrument': 'EUR_USD', 'units': '100.0', 'gainQuoteHomeConversionFactor': '0.835888606316', 'lossQuoteHomeConversionFactor': '0.844289496832', 'price': 1.19041, 'fullVWAP': 1.19041, 'fullPrice': {'type': 'PRICE', 'bids': [{'price': 1.19029, 'liquidity': '10000000'}], 'asks': [{'price': 1.19041, 'liquidity': '10000000'}], 'closeoutBid': 1.19029, 'closeoutAsk': 1.19041}, 'reason': 'MARKET_ORDER', 'pl': '0.0', 'financing': '0.0', 'commission': '0.0', 'guaranteedExecutionFee': '0.0', 'accountBalance': '98137.7694', 'tradeOpened': {'tradeID': '2736', 'units': '100.0', 'price': 1.19041, 'guaranteedExecutionFee': '0.0', 'halfSpreadCost': '0.005', 'initialMarginRequired': '3.33'}, 'halfSpreadCost': '0.005'} 
    



```python
# closing out the position
oanda.create_order('EUR_USD', units=-100)
```

    
    
     {'id': '2739', 'time': '2021-06-22T06:47:57.539914287Z', 'userID': 13834683, 'accountID': '101-004-13834683-001', 'batchID': '2738', 'requestID': '78870588578569980', 'type': 'ORDER_FILL', 'orderID': '2738', 'instrument': 'EUR_USD', 'units': '-100.0', 'gainQuoteHomeConversionFactor': '0.835888606316', 'lossQuoteHomeConversionFactor': '0.844289496832', 'price': 1.19029, 'fullVWAP': 1.19029, 'fullPrice': {'type': 'PRICE', 'bids': [{'price': 1.19029, 'liquidity': '10000000'}], 'asks': [{'price': 1.19041, 'liquidity': '9999900'}], 'closeoutBid': 1.19029, 'closeoutAsk': 1.19041}, 'reason': 'MARKET_ORDER', 'pl': '-0.0107', 'financing': '0.0', 'commission': '0.0', 'guaranteedExecutionFee': '0.0', 'accountBalance': '98137.7587', 'tradesClosed': [{'tradeID': '2730', 'units': '-60.0', 'price': 1.19029, 'realizedPL': '-0.0066', 'financing': '0.0', 'guaranteedExecutionFee': '0.0', 'halfSpreadCost': '0.003'}], 'tradeReduced': {'tradeID': '2736', 'units': '-40.0', 'price': 1.19029, 'realizedPL': '-0.0041', 'financing': '0.0', 'guaranteedExecutionFee': '0.0', 'halfSpreadCost': '0.002'}, 'halfSpreadCost': '0.005'} 
    



```python
help(oanda.get_account_summary)
```

    Help on method get_account_summary in module tpqoa.tpqoa:
    
    get_account_summary(detailed=False) method of tpqoa.tpqoa.tpqoa instance
        Returns summary data for Oanda account.
    



```python
oanda.get_account_summary()
```




    {'id': '101-004-13834683-001',
     'alias': 'Primary',
     'currency': 'EUR',
     'balance': '98137.7587',
     'createdByUserID': 13834683,
     'createdTime': '2020-03-19T06:08:14.363139403Z',
     'guaranteedStopLossOrderMode': 'DISABLED',
     'pl': '-1584.9266',
     'resettablePL': '-1584.9266',
     'resettablePLTime': '0',
     'financing': '-277.3147',
     'commission': '0.0',
     'guaranteedExecutionFees': '0.0',
     'marginRate': '0.0333',
     'openTradeCount': 2,
     'openPositionCount': 2,
     'pendingOrderCount': 1,
     'hedgingEnabled': False,
     'unrealizedPL': '3453.802',
     'NAV': '101591.5607',
     'marginUsed': '633.598',
     'marginAvailable': '100975.1437',
     'positionValue': '6376.0',
     'marginCloseoutUnrealizedPL': '3472.4211',
     'marginCloseoutNAV': '101610.1798',
     'marginCloseoutMarginUsed': '633.598',
     'marginCloseoutPercent': '0.00312',
     'marginCloseoutPositionValue': '6376.0',
     'withdrawalLimit': '98137.7587',
     'marginCallMarginUsed': '633.598',
     'marginCallPercent': '0.00624',
     'lastTransactionID': '2740'}




```python
help(oanda.get_transactions)
```

    Help on method get_transactions in module tpqoa.tpqoa:
    
    get_transactions(tid=0) method of tpqoa.tpqoa.tpqoa instance
        Retrieves and returns transactions data.
    



```python
help(oanda.print_transactions)
```

    Help on method print_transactions in module tpqoa.tpqoa:
    
    print_transactions(tid=0) method of tpqoa.tpqoa.tpqoa instance
        Prints basic transactions data.
    



```python
oanda.print_transactions(tid=2700)
```

    2701 | 2021-06-22T06:35:55.79 | EUR_USD |     10.0 |      0.0
    2704 | 2021-06-22T06:35:56.12 | EUR_USD |     10.0 |      0.0
    2707 | 2021-06-22T06:38:06.06 | EUR_USD |     10.0 |      0.0
    2709 | 2021-06-22T06:38:06.41 | EUR_USD |     10.0 |      0.0
    2712 | 2021-06-22T06:38:06.74 | EUR_USD |     10.0 |      0.0
    2715 | 2021-06-22T06:40:52.40 | EUR_USD |    100.0 |      0.0
    2718 | 2021-06-22T06:40:53.96 | EUR_USD |   -100.0 |  -0.0048
    2724 | 2021-06-22T06:44:24.04 | EUR_USD |    100.0 |      0.0
    2727 | 2021-06-22T06:44:24.23 | EUR_USD |   -100.0 |   0.0088
    2730 | 2021-06-22T06:47:37.13 | EUR_USD |    100.0 |      0.0
    2733 | 2021-06-22T06:47:37.30 | EUR_USD |   -100.0 |  -0.0062
    2736 | 2021-06-22T06:47:57.37 | EUR_USD |    100.0 |      0.0
    2739 | 2021-06-22T06:47:57.53 | EUR_USD |   -100.0 |  -0.0107


<img src="http://hilpisch.com/tpq_logo.png" alt="The Python Quants" width="35%" align="right" border="0"><br>

<a href="http://tpq.io" target="_blank">http://tpq.io</a> | <a href="http://twitter.com/dyjh" target="_blank">@dyjh</a> | <a href="mailto:training@tpq.io">training@tpq.io</a>
