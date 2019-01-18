
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




    [('USD/CNH', 'USD_CNH'),
     ('Gold/CAD', 'XAU_CAD'),
     ('US 2Y T-Note', 'USB02Y_USD'),
     ('India 50', 'IN50_USD'),
     ('Gold/AUD', 'XAU_AUD'),
     ('EUR/HKD', 'EUR_HKD'),
     ('Silver/HKD', 'XAG_HKD'),
     ('Silver/AUD', 'XAG_AUD'),
     ('Japan 225', 'JP225_USD'),
     ('US SPX 500', 'SPX500_USD')]



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
                  start='2018-01-01',
                  end='2018-08-09',
                  granularity='D',
                  price='A')
```


```python
data.info()
```

    <class 'pandas.core.frame.DataFrame'>
    DatetimeIndex: 158 entries, 2018-01-01 22:00:00 to 2018-08-08 21:00:00
    Data columns (total 6 columns):
    c           158 non-null float64
    complete    158 non-null bool
    h           158 non-null float64
    l           158 non-null float64
    o           158 non-null float64
    volume      158 non-null int64
    dtypes: bool(1), float64(4), int64(1)
    memory usage: 7.6 KB



```python
print(data.head())
```

                               c complete        h        l        o  volume
    time                                                                    
    2018-01-01 22:00:00  1.20610     True  1.20819  1.20051  1.20101   35630
    2018-01-02 22:00:00  1.20170     True  1.20673  1.20018  1.20620   31354
    2018-01-03 22:00:00  1.20710     True  1.20897  1.20049  1.20170   35187
    2018-01-04 22:00:00  1.20327     True  1.20847  1.20215  1.20692   36478
    2018-01-07 22:00:00  1.19717     True  1.20530  1.19564  1.20301   27618


## Streaming Data

The method `stream_data()` allows the streaming of real-time data (bid & ask).


```python
oanda.stream_data('EUR_USD', stop=3)
```

    2019-01-18T08:27:48.293661969Z 1.13965 1.13977
    2019-01-18T08:27:53.849941883Z 1.13968 1.1398
    2019-01-18T08:27:54.944929674Z 1.13967 1.1398


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

    BID: 1.13960 | ASK: 1.13973
    BID: 1.13961 | ASK: 1.13974
    BID: 1.13965 | ASK: 1.13979
    BID: 1.13961 | ASK: 1.13974
    BID: 1.13958 | ASK: 1.13970


## Other Methods

Other major methods are:


```python
help(oanda.create_order)
```

    Help on method create_order in module tpqoa.tpqoa:
    
    create_order(instrument, units, sl_distance=0.01) method of tpqoa.tpqoa.tpqoa instance
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
    



```python
# going long 10,000 units
# sl_distance of 20 pips
oanda.create_order('EUR_USD', units=10000, sl_distance=0.002)
```

    
    
     {'id': '3279', 'time': '2019-01-18T08:28:16.376958880Z', 'userID': 5516121, 'accountID': '101-004-5516121-001', 'batchID': '3278', 'requestID': '42520741153607542', 'type': 'ORDER_FILL', 'orderID': '3278', 'instrument': 'EUR_USD', 'units': '10000.0', 'gainQuoteHomeConversionFactor': '0.877408486295', 'lossQuoteHomeConversionFactor': '0.877516277927', 'price': 1.13972, 'fullVWAP': 1.13972, 'fullPrice': {'type': 'PRICE', 'bids': [{'price': 1.13958, 'liquidity': '10000000'}], 'asks': [{'price': 1.13972, 'liquidity': '10000000'}], 'closeoutBid': 1.13943, 'closeoutAsk': 1.13987}, 'reason': 'MARKET_ORDER', 'pl': '0.0', 'financing': '0.0', 'commission': '0.0', 'guaranteedExecutionFee': '0.0', 'accountBalance': '97127.3433', 'tradeOpened': {'tradeID': '3279', 'units': '10000.0', 'price': 1.13972, 'guaranteedExecutionFee': '0.0', 'halfSpreadCost': '0.6142', 'initialMarginRequired': '333.0'}, 'halfSpreadCost': '0.6142'} 
    



```python
# closing out the position
oanda.create_order('EUR_USD', units=-10000)
```

    
    
     {'id': '3282', 'time': '2019-01-18T08:28:36.645117858Z', 'userID': 5516121, 'accountID': '101-004-5516121-001', 'batchID': '3281', 'requestID': '42520741237523586', 'type': 'ORDER_FILL', 'orderID': '3281', 'instrument': 'EUR_USD', 'units': '-10000.0', 'gainQuoteHomeConversionFactor': '0.877277632052', 'lossQuoteHomeConversionFactor': '0.87737769355', 'price': 1.13976, 'fullVWAP': 1.13976, 'fullPrice': {'type': 'PRICE', 'bids': [{'price': 1.13976, 'liquidity': '10000000'}], 'asks': [{'price': 1.13989, 'liquidity': '10000000'}], 'closeoutBid': 1.13961, 'closeoutAsk': 1.14004}, 'reason': 'MARKET_ORDER', 'pl': '0.3509', 'financing': '-0.0003', 'commission': '0.0', 'guaranteedExecutionFee': '0.0', 'accountBalance': '97127.6939', 'tradesClosed': [{'tradeID': '3279', 'units': '-10000.0', 'price': 1.13976, 'realizedPL': '0.3509', 'financing': '-0.0003', 'guaranteedExecutionFee': '0.0', 'halfSpreadCost': '0.5703'}], 'halfSpreadCost': '0.5703'} 
    



```python
help(oanda.get_account_summary)
```

    Help on method get_account_summary in module tpqoa.tpqoa:
    
    get_account_summary(detailed=False) method of tpqoa.tpqoa.tpqoa instance
        Returns summary data for Oanda account.
    



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
oanda.print_transactions(tid=3272)
```

     3273 | 2019-01-18T08:24:37.037381266Z |   EUR_USD |         10.0 |      0.0
     3276 | 2019-01-18T08:26:03.380025696Z |   EUR_USD |        -10.0 |  -0.0022
     3279 | 2019-01-18T08:28:16.376958880Z |   EUR_USD |      10000.0 |      0.0
     3282 | 2019-01-18T08:28:36.645117858Z |   EUR_USD |     -10000.0 |   0.3509


<img src="http://hilpisch.com/tpq_logo.png" alt="The Python Quants" width="35%" align="right" border="0"><br>

<a href="http://tpq.io" target="_blank">http://tpq.io</a> | <a href="http://twitter.com/dyjh" target="_blank">@dyjh</a> | <a href="mailto:training@tpq.io">training@tpq.io</a>
