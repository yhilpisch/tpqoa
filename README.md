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

    pip install git+git://github.com/yhilpisch/tpqoa

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
oanda = tpqoa.tpqoa('../../oanda.cfg')  # adjust path as necessary
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
# oanda.get_history??
```


```python
data = oanda.get_history(instrument='EUR_USD',
                  start='2022-06-15',
                  end='2023-06-15',
                  granularity='D',
                  price='M')
```


```python
data.info()
```

    <class 'pandas.core.frame.DataFrame'>
    DatetimeIndex: 261 entries, 2022-06-14 21:00:00 to 2023-06-14 21:00:00
    Data columns (total 6 columns):
     #   Column    Non-Null Count  Dtype  
    ---  ------    --------------  -----  
     0   o         261 non-null    float64
     1   h         261 non-null    float64
     2   l         261 non-null    float64
     3   c         261 non-null    float64
     4   volume    261 non-null    int64  
     5   complete  261 non-null    bool   
    dtypes: bool(1), float64(4), int64(1)
    memory usage: 12.5 KB



```python
print(data.head())
```

                               o        h        l        c  volume  complete
    time                                                                     
    2022-06-14 21:00:00  1.04114  1.05078  1.03593  1.04466  204826      True
    2022-06-15 21:00:00  1.04444  1.06014  1.03809  1.05524  183417      True
    2022-06-16 21:00:00  1.05496  1.05612  1.04445  1.04938  156233      True
    2022-06-19 21:00:00  1.04841  1.05460  1.04746  1.05112   85713      True
    2022-06-20 21:00:00  1.05088  1.05826  1.05086  1.05348  101517      True


## Streaming Data

The method `stream_data()` allows the streaming of real-time data (bid & ask).


```python
oanda.stream_data('EUR_USD', stop=3)
```

    2023-06-27T06:57:58.204324464Z 1.09299 1.09313
    2023-06-27T06:57:58.400409926Z 1.09301 1.09315
    2023-06-27T06:58:00.348284643Z 1.093 1.09314


By redefining the `on_success()` method, you can control what happes with the streaming data.


```python
class myOanda(tpqoa.tpqoa):
    def on_success(self, time, bid, ask):
        ''' Method called when new data is retrieved. '''
        print('BID: {:.5f} | ASK: {:.5f}'.format(bid, ask))
```


```python
my_oanda = myOanda('../../oanda.cfg')
```


```python
my_oanda.stream_data('EUR_USD', stop=5)
```

    BID: 1.09297 | ASK: 1.09311
    BID: 1.09297 | ASK: 1.09310
    BID: 1.09297 | ASK: 1.09311
    BID: 1.09297 | ASK: 1.09312
    BID: 1.09294 | ASK: 1.09309


## Placing Orders


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

    
    
     {'id': '3608', 'time': '2023-06-27T06:58:16.307275954Z', 'userID': 13834683, 'accountID': '101-004-13834683-001', 'batchID': '3607', 'requestID': '61122547747050135', 'type': 'ORDER_FILL', 'orderID': '3607', 'instrument': 'EUR_USD', 'units': '100.0', 'gainQuoteHomeConversionFactor': '0.910326029089', 'lossQuoteHomeConversionFactor': '0.919475034407', 'price': 1.09309, 'fullVWAP': 1.09309, 'fullPrice': {'type': 'PRICE', 'bids': [{'price': 1.09294, 'liquidity': '10000000'}], 'asks': [{'price': 1.09309, 'liquidity': '10000000'}], 'closeoutBid': 1.09294, 'closeoutAsk': 1.09309}, 'reason': 'MARKET_ORDER', 'pl': '0.0', 'financing': '0.0', 'commission': '0.0', 'guaranteedExecutionFee': '0.0', 'accountBalance': '101295.189', 'tradeOpened': {'tradeID': '3608', 'units': '100.0', 'price': 1.09309, 'guaranteedExecutionFee': '0.0', 'halfSpreadCost': '0.0069', 'initialMarginRequired': '3.33'}, 'halfSpreadCost': '0.0069'} 
    



```python
# closing out the position
oanda.create_order('EUR_USD', units=-100)
```

    
    
     {'id': '3611', 'time': '2023-06-27T06:58:16.523945599Z', 'userID': 13834683, 'accountID': '101-004-13834683-001', 'batchID': '3610', 'requestID': '61122547747050332', 'type': 'ORDER_FILL', 'orderID': '3610', 'instrument': 'EUR_USD', 'units': '-100.0', 'gainQuoteHomeConversionFactor': '0.910326029089', 'lossQuoteHomeConversionFactor': '0.919475034407', 'price': 1.09294, 'fullVWAP': 1.09294, 'fullPrice': {'type': 'PRICE', 'bids': [{'price': 1.09294, 'liquidity': '10000000'}], 'asks': [{'price': 1.09309, 'liquidity': '9999900'}], 'closeoutBid': 1.09294, 'closeoutAsk': 1.09309}, 'reason': 'MARKET_ORDER', 'pl': '-0.0138', 'financing': '0.0', 'commission': '0.0', 'guaranteedExecutionFee': '0.0', 'accountBalance': '101295.1752', 'tradesClosed': [{'tradeID': '3608', 'units': '-100.0', 'price': 1.09294, 'realizedPL': '-0.0138', 'financing': '0.0', 'guaranteedExecutionFee': '0.0', 'halfSpreadCost': '0.0069'}], 'halfSpreadCost': '0.0069'} 
    


## Canceling Orders 


```python
order = oanda.create_order('EUR_USD', units=10000, sl_distance=0.01, ret=True)
```

    
    
     {'id': '3614', 'time': '2023-06-27T06:58:33.953341530Z', 'userID': 13834683, 'accountID': '101-004-13834683-001', 'batchID': '3613', 'requestID': '61122547818369950', 'type': 'ORDER_FILL', 'orderID': '3613', 'instrument': 'EUR_USD', 'units': '10000.0', 'gainQuoteHomeConversionFactor': '0.910363508679', 'lossQuoteHomeConversionFactor': '0.919512890676', 'price': 1.09304, 'fullVWAP': 1.09304, 'fullPrice': {'type': 'PRICE', 'bids': [{'price': 1.0929, 'liquidity': '10000000'}], 'asks': [{'price': 1.09304, 'liquidity': '10000000'}], 'closeoutBid': 1.0929, 'closeoutAsk': 1.09304}, 'reason': 'MARKET_ORDER', 'pl': '0.0', 'financing': '0.0', 'commission': '0.0', 'guaranteedExecutionFee': '0.0', 'accountBalance': '101295.1752', 'tradeOpened': {'tradeID': '3614', 'units': '10000.0', 'price': 1.09304, 'guaranteedExecutionFee': '0.0', 'halfSpreadCost': '0.6405', 'initialMarginRequired': '333.0'}, 'halfSpreadCost': '0.6405'} 
    



```python
oanda.get_transaction(tid=int(order['id']) + 1)
```




    {'id': '3615',
     'time': '2023-06-27T06:58:33.953341530Z',
     'userID': 13834683,
     'accountID': '101-004-13834683-001',
     'batchID': '3613',
     'requestID': '61122547818369950',
     'type': 'STOP_LOSS_ORDER',
     'tradeID': '3614',
     'price': 1.08304,
     'distance': '0.01',
     'timeInForce': 'GTC',
     'triggerCondition': 'DEFAULT',
     'reason': 'ON_FILL'}




```python
oanda.cancel_order(int(order['id']) + 1)
```




    {'orderCancelTransaction': {'id': '3616',
      'accountID': '101-004-13834683-001',
      'userID': 13834683,
      'batchID': '3616',
      'requestID': '61122547826759581',
      'time': '2023-06-27T06:58:35.038788414Z',
      'type': 'ORDER_CANCEL',
      'orderID': '3615',
      'reason': 'CLIENT_REQUEST'},
     'relatedTransactionIDs': ['3616'],
     'lastTransactionID': '3616'}




```python
order = oanda.create_order('EUR_USD', units=-10000)
```

    
    
     {'id': '3618', 'time': '2023-06-27T06:58:36.381641548Z', 'userID': 13834683, 'accountID': '101-004-13834683-001', 'batchID': '3617', 'requestID': '61122547830955203', 'type': 'ORDER_FILL', 'orderID': '3617', 'instrument': 'EUR_USD', 'units': '-10000.0', 'gainQuoteHomeConversionFactor': '0.910359343552', 'lossQuoteHomeConversionFactor': '0.919508683689', 'price': 1.09291, 'fullVWAP': 1.09291, 'fullPrice': {'type': 'PRICE', 'bids': [{'price': 1.09291, 'liquidity': '10000000'}], 'asks': [{'price': 1.09304, 'liquidity': '9990000'}], 'closeoutBid': 1.09291, 'closeoutAsk': 1.09304}, 'reason': 'MARKET_ORDER', 'pl': '-1.1954', 'financing': '0.0', 'commission': '0.0', 'guaranteedExecutionFee': '0.0', 'accountBalance': '101293.9798', 'tradesClosed': [{'tradeID': '3614', 'units': '-10000.0', 'price': 1.09291, 'realizedPL': '-1.1954', 'financing': '0.0', 'guaranteedExecutionFee': '0.0', 'halfSpreadCost': '0.5947'}], 'halfSpreadCost': '0.5947'} 
    


## Account-Related Methods


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
     'balance': '101293.9798',
     'createdByUserID': 13834683,
     'createdTime': '2020-03-19T06:08:14.363139403Z',
     'guaranteedStopLossOrderMode': 'ALLOWED',
     'pl': '1488.9357',
     'resettablePL': '1488.9357',
     'resettablePLTime': '0',
     'financing': '-194.9559',
     'commission': '0.0',
     'guaranteedExecutionFees': '0.0',
     'marginRate': '0.0333',
     'openTradeCount': 0,
     'openPositionCount': 0,
     'pendingOrderCount': 0,
     'hedgingEnabled': False,
     'unrealizedPL': '0.0',
     'NAV': '101293.9798',
     'marginUsed': '0.0',
     'marginAvailable': '101293.9798',
     'positionValue': '0.0',
     'marginCloseoutUnrealizedPL': '0.0',
     'marginCloseoutNAV': '101293.9798',
     'marginCloseoutMarginUsed': '0.0',
     'marginCloseoutPercent': '0.0',
     'marginCloseoutPositionValue': '0.0',
     'withdrawalLimit': '101293.9798',
     'marginCallMarginUsed': '0.0',
     'marginCallPercent': '0.0',
     'lastTransactionID': '3618'}




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
oanda.print_transactions(tid=3545)
```

    3547 | 2023-06-27T06:07:18.75 | EUR_USD | -10000.0 |   2.0954
    3550 | 2023-06-27T06:12:25.19 | EUR_USD |  10000.0 |      0.0
    3553 | 2023-06-27T06:37:02.60 | EUR_USD | -10000.0 |   3.0046
    3556 | 2023-06-27T06:39:10.34 | EUR_USD |    100.0 |      0.0
    3559 | 2023-06-27T06:39:10.50 | EUR_USD |   -100.0 |  -0.0129
    3562 | 2023-06-27T06:39:34.89 | EUR_USD |  10000.0 |      0.0
    3568 | 2023-06-27T06:43:59.81 | EUR_USD | -10000.0 |  -1.5631
    3570 | 2023-06-27T06:44:08.72 | EUR_USD |  10000.0 |      0.0
    3574 | 2023-06-27T06:52:58.26 | EUR_USD |    100.0 |      0.0
    3577 | 2023-06-27T06:52:58.45 | EUR_USD |   -100.0 |  -0.0451
    3579 | 2023-06-27T06:53:12.67 | EUR_USD |  10000.0 |      0.0
    3583 | 2023-06-27T06:54:17.23 | EUR_USD | -10000.0 |  -4.9358
    3586 | 2023-06-27T06:54:20.61 | EUR_USD |  10000.0 |      0.0
    3590 | 2023-06-27T06:56:29.21 | EUR_USD |    100.0 |      0.0
    3593 | 2023-06-27T06:56:29.42 | EUR_USD |   -100.0 |   0.0246
    3595 | 2023-06-27T06:56:29.63 | EUR_USD |  10000.0 |      0.0
    3599 | 2023-06-27T06:56:30.24 | EUR_USD | -10000.0 |   2.0921
    3601 | 2023-06-27T06:57:23.19 | EUR_USD | -10000.0 |    0.091
    3603 | 2023-06-27T06:57:27.47 | EUR_USD |   -100.0 |  -0.0074
    3606 | 2023-06-27T06:57:33.23 | EUR_USD |  -9900.0 |   3.1541
    3608 | 2023-06-27T06:58:16.30 | EUR_USD |    100.0 |      0.0
    3611 | 2023-06-27T06:58:16.52 | EUR_USD |   -100.0 |  -0.0138
    3614 | 2023-06-27T06:58:33.95 | EUR_USD |  10000.0 |      0.0
    3618 | 2023-06-27T06:58:36.38 | EUR_USD | -10000.0 |  -1.1954


<img src="http://hilpisch.com/tpq_logo.png" alt="The Python Quants" width="35%" align="right" border="0"><br>

<a href="http://tpq.io" target="_blank">http://tpq.io</a> | <a href="http://twitter.com/dyjh" target="_blank">@dyjh</a> | <a href="mailto:training@tpq.io">training@tpq.io</a>
