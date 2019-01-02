
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




    [('TRY/JPY', 'TRY_JPY'),
     ('USD/THB', 'USD_THB'),
     ('GBP/CHF', 'GBP_CHF'),
     ('CHF/HKD', 'CHF_HKD'),
     ('Gold/NZD', 'XAU_NZD'),
     ('Gold/Silver', 'XAU_XAG'),
     ('AUD/CAD', 'AUD_CAD'),
     ('SGD/JPY', 'SGD_JPY'),
     ('AUD/USD', 'AUD_USD'),
     ('Silver/JPY', 'XAG_JPY')]



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

    2019-01-02T10:48:57.792678945Z 1.14374 1.14387
    2019-01-02T10:49:21.500587626Z 1.14377 1.14391
    2019-01-02T10:49:23.730787714Z 1.14379 1.14392


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
my_oanda.stream_data('EUR_USD', stop=7)
```

    BID: 1.14379 | ASK: 1.14392
    BID: 1.14382 | ASK: 1.14396
    BID: 1.14380 | ASK: 1.14394
    BID: 1.14377 | ASK: 1.14389
    BID: 1.14373 | ASK: 1.14386
    BID: 1.14369 | ASK: 1.14383
    BID: 1.14374 | ASK: 1.14386


## Other Methods

Other major methods are:


```python
help(oanda.create_order)
```

    Help on method create_order in module tpqoa.tpqoa:
    
    create_order(instrument, units) method of tpqoa.tpqoa.tpqoa instance
        Places order with Oanda.
        
        Parameters
        ==========
        instrument: string
            valid instrument name
        units: int
            number of units of instrument to be bought
            (positive int, eg 'units=50')
            or to be sold (negative int, eg 'units=-100')
    



```python
help(oanda.get_transactions)
```

    Help on method get_transactions in module tpqoa.tpqoa:
    
    get_transactions(tid=0) method of tpqoa.tpqoa.tpqoa instance
        Retrieves and returns transactions data.
    



```python
help(oanda.get_account_summary)
```

    Help on method get_account_summary in module tpqoa.tpqoa:
    
    get_account_summary(detailed=False) method of tpqoa.tpqoa.tpqoa instance
        Returns summary data for Oanda account.
    



```python
help(oanda.print_transactions)
```

    Help on method print_transactions in module tpqoa.tpqoa:
    
    print_transactions(tid=0) method of tpqoa.tpqoa.tpqoa instance
        Prints basic transactions data.
    



```python
oanda.print_transactions(tid=3175)
```

     3177 | 2018-09-28T07:59:44.972093309Z |   EUR_USD |     -99500.0 | -27.3996
     3179 | 2018-09-28T08:03:24.441630523Z |   EUR_USD |       1000.0 |      0.0
     3181 | 2018-09-28T08:03:24.568658352Z |   EUR_USD |      -1500.0 |  -0.1119
     3183 | 2018-09-28T08:03:24.699807529Z |   EUR_USD |        500.0 |  -0.0559
     3185 | 2018-09-28T08:04:50.888923319Z |   EUR_USD |    -100000.0 |      0.0
     3187 | 2018-09-28T08:05:30.543503420Z |   EUR_USD |     200000.0 | -12.0516
     3189 | 2018-09-28T08:06:06.795250575Z |   EUR_USD |    -100000.0 |  -2.5823
     3191 | 2018-11-15T15:06:41.181894512Z |   EUR_USD |        200.0 |      0.0


<img src="http://hilpisch.com/tpq_logo.png" alt="The Python Quants" width="35%" align="right" border="0"><br>

<a href="http://tpq.io" target="_blank">http://tpq.io</a> | <a href="http://twitter.com/dyjh" target="_blank">@dyjh</a> | <a href="mailto:training@tpq.io">training@tpq.io</a>
