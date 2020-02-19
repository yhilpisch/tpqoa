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

Using `pip` directly:

    pip install --index-url https://test.pypi.org/simple/ tpqoa

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




    [('Silver/CHF', 'XAG_CHF'),
     ('Silver/EUR', 'XAG_EUR'),
     ('UK 10Y Gilt', 'UK10YB_GBP'),
     ('GBP/ZAR', 'GBP_ZAR'),
     ('Soybeans', 'SOYBN_USD'),
     ('NZD/SGD', 'NZD_SGD'),
     ('USD/HKD', 'USD_HKD'),
     ('GBP/PLN', 'GBP_PLN'),
     ('Platinum', 'XPT_USD'),
     ('USD/JPY', 'USD_JPY')]



## Historical Data

The `get_history()` method retrieves historical data.


```python
help(oanda.get_history)
```

    Help on method get_history in module tpqoa.tpqoa:
    
    get_history(instrument, start, end, granularity, price) method of tpqoa.tpqoa.tpqoa instance
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
            one of 'A' (ask) or 'B' (bid)
        
        Returns
        =======
        data: pd.DataFrame
            pandas DataFrame object with data
    



```python
data = oanda.get_history(instrument='EUR_USD',
                  start='2019-07-01',
                  end='2020-01-31',
                  granularity='D',
                  price='A')
```


```python
data.info()
```

    <class 'pandas.core.frame.DataFrame'>
    DatetimeIndex: 154 entries, 2019-06-30 21:00:00+00:00 to 2020-01-30 22:00:00+00:00
    Data columns (total 6 columns):
    volume      154 non-null int64
    complete    154 non-null bool
    o           154 non-null float64
    h           154 non-null float64
    l           154 non-null float64
    c           154 non-null float64
    dtypes: bool(1), float64(4), int64(1)
    memory usage: 7.4 KB



```python
print(data.head())
```

                               volume  complete        o        h        l  \
    time                                                                     
    2019-06-30 21:00:00+00:00   18780      True  1.13644  1.13721  1.12819   
    2019-07-01 21:00:00+00:00   15567      True  1.12867  1.13233  1.12759   
    2019-07-02 21:00:00+00:00   14593      True  1.12871  1.13139  1.12695   
    2019-07-03 21:00:00+00:00    5731      True  1.12795  1.12960  1.12740   
    2019-07-04 21:00:00+00:00   15161      True  1.12871  1.12885  1.12081   
    
                                     c  
    time                                
    2019-06-30 21:00:00+00:00  1.12867  
    2019-07-01 21:00:00+00:00  1.12871  
    2019-07-02 21:00:00+00:00  1.12797  
    2019-07-03 21:00:00+00:00  1.12859  
    2019-07-04 21:00:00+00:00  1.12305  


## Streaming Data

The method `stream_data()` allows the streaming of real-time data (bid & ask).


```python
oanda.stream_data('EUR_USD', stop=3)
```

    2020-02-19T15:58:29.459179673Z 1.07937 1.07949
    2020-02-19T15:58:31.140133526Z 1.07935 1.07947
    2020-02-19T15:58:31.290597325Z 1.07937 1.07948


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

    BID: 1.07937 | ASK: 1.07949
    BID: 1.07939 | ASK: 1.07949
    BID: 1.07938 | ASK: 1.07948
    BID: 1.07939 | ASK: 1.07949
    BID: 1.07940 | ASK: 1.07952


## Other Methods

Other major methods are:


```python
help(oanda.create_order)
```

    Help on method create_order in module tpqoa.tpqoa:
    
    create_order(instrument, units, sl_distance=None, tsl_distance=None, tp_price=None, comment=None) method of tpqoa.tpqoa.tpqoa instance
        Places order with Oanda.
        
        Parameters
        ==========
        instrument: string
            valid instrument name
        units: int
            number of units of instrument to be bought
            (positive int, eg 'units=50')
            or to be sold (negative int, eg 'units=-100')
        sl_distance: float
            stop loss distance price, mandatory eg in Germany
        tsl_distance: float
            trailing stop loss distance
        tp_price: float
            take profit price to be used for the trade
        comment: str
            string
    



```python
# going long 100 units
# sl_distance of 20 pips
oanda.create_order('EUR_USD', units=100, sl_distance=0.002)
```

    
    
     {'id': '4344', 'time': '2020-02-19T15:58:35.938800989Z', 'userID': 5516121, 'accountID': '101-004-5516121-001', 'batchID': '4343', 'requestID': '60679120971548823', 'type': 'ORDER_FILL', 'orderID': '4343', 'instrument': 'EUR_USD', 'units': '100.0', 'gainQuoteHomeConversionFactor': '0.926363375298', 'lossQuoteHomeConversionFactor': '0.926457781319', 'price': 1.07949, 'fullVWAP': 1.07949, 'fullPrice': {'type': 'PRICE', 'bids': [{'price': 1.07938, 'liquidity': '10000000'}], 'asks': [{'price': 1.07949, 'liquidity': '10000000'}], 'closeoutBid': 1.07938, 'closeoutAsk': 1.07949}, 'reason': 'MARKET_ORDER', 'pl': '0.0', 'financing': '0.0', 'commission': '0.0', 'guaranteedExecutionFee': '0.0', 'accountBalance': '96758.9083', 'tradeOpened': {'tradeID': '4344', 'units': '100.0', 'price': 1.07949, 'guaranteedExecutionFee': '0.0', 'halfSpreadCost': '0.0051', 'initialMarginRequired': '5.0'}, 'halfSpreadCost': '0.0051'} 
    





    <v20.response.Response at 0x121be1510>




```python
# closing out the position
oanda.create_order('EUR_USD', units=-100)
```

    
    
     {'id': '4347', 'time': '2020-02-19T15:58:36.084702016Z', 'userID': 5516121, 'accountID': '101-004-5516121-001', 'batchID': '4346', 'requestID': '60679120975743546', 'type': 'ORDER_FILL', 'orderID': '4346', 'instrument': 'EUR_USD', 'units': '-100.0', 'gainQuoteHomeConversionFactor': '0.926363375298', 'lossQuoteHomeConversionFactor': '0.926457781319', 'price': 1.07938, 'fullVWAP': 1.07938, 'fullPrice': {'type': 'PRICE', 'bids': [{'price': 1.07938, 'liquidity': '10000000'}], 'asks': [{'price': 1.07949, 'liquidity': '9999900'}], 'closeoutBid': 1.07938, 'closeoutAsk': 1.07949}, 'reason': 'MARKET_ORDER', 'pl': '-0.0102', 'financing': '0.0', 'commission': '0.0', 'guaranteedExecutionFee': '0.0', 'accountBalance': '96758.8981', 'tradesClosed': [{'tradeID': '4344', 'units': '-100.0', 'price': 1.07938, 'realizedPL': '-0.0102', 'financing': '0.0', 'guaranteedExecutionFee': '0.0', 'halfSpreadCost': '0.0051'}], 'halfSpreadCost': '0.0051'} 
    





    <v20.response.Response at 0x121b68710>




```python
help(oanda.get_account_summary)
```

    Help on method get_account_summary in module tpqoa.tpqoa:
    
    get_account_summary(detailed=False) method of tpqoa.tpqoa.tpqoa instance
        Returns summary data for Oanda account.
    



```python
oanda.get_account_summary()
```




    {'id': '101-004-5516121-001',
     'alias': 'Primary',
     'currency': 'EUR',
     'balance': '96758.8981',
     'createdByUserID': 5516121,
     'createdTime': '2017-03-08T16:28:21.276100637Z',
     'guaranteedStopLossOrderMode': 'DISABLED',
     'pl': '-121958.3379',
     'resettablePL': '-121958.3379',
     'resettablePLTime': '2017-03-08T16:28:21.276100637Z',
     'financing': '-704.944',
     'commission': '0.0',
     'guaranteedExecutionFees': '0.0',
     'marginRate': '0.05',
     'openTradeCount': 0,
     'openPositionCount': 0,
     'pendingOrderCount': 0,
     'hedgingEnabled': False,
     'unrealizedPL': '0.0',
     'NAV': '96758.8981',
     'marginUsed': '0.0',
     'marginAvailable': '96758.8981',
     'positionValue': '0.0',
     'marginCloseoutUnrealizedPL': '0.0',
     'marginCloseoutNAV': '96758.8981',
     'marginCloseoutMarginUsed': '0.0',
     'marginCloseoutPercent': '0.0',
     'marginCloseoutPositionValue': '0.0',
     'withdrawalLimit': '96758.8981',
     'marginCallMarginUsed': '0.0',
     'marginCallPercent': '0.0',
     'lastTransactionID': '4348'}




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
oanda.print_transactions(tid=4300)
```

     4303 | 2020-01-13T13:58:21.608898271Z |   EUR_GBP |       -100.0 |    0.007
     4316 | 2020-01-24T12:57:49.782136872Z |   EUR_USD |       -100.0 |  -0.9069
     4317 | 2020-01-24T12:57:49.829755813Z |   EUR_USD |       -100.0 |   -0.907
     4321 | 2020-01-27T15:45:00.969811653Z |   EUR_USD |       -100.0 |   -0.908
     4336 | 2020-02-10T15:57:40.773642237Z |   EUR_USD |      -9500.0 | -86.9947
     4338 | 2020-02-19T15:56:27.193640467Z |   EUR_USD |        100.0 |      0.0
     4341 | 2020-02-19T15:56:39.259782926Z |   EUR_USD |       -100.0 |  -0.0065
     4344 | 2020-02-19T15:58:35.938800989Z |   EUR_USD |        100.0 |      0.0
     4347 | 2020-02-19T15:58:36.084702016Z |   EUR_USD |       -100.0 |  -0.0102


<img src="http://hilpisch.com/tpq_logo.png" alt="The Python Quants" width="35%" align="right" border="0"><br>

<a href="http://tpq.io" target="_blank">http://tpq.io</a> | <a href="http://twitter.com/dyjh" target="_blank">@dyjh</a> | <a href="mailto:training@tpq.io">training@tpq.io</a>
