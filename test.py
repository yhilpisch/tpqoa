#
# tpqoa is a wrapper class for the
# Oanda v20 API (RESTful & streaming)
# making use of the v20 Python package
#
# Test Suite
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

import unittest
from time import sleep
from decimal import Decimal

from tpqoa import tpqoa


class TestTPQOA(unittest.TestCase):

    def setUp(self):
        self.tpqoa = tpqoa('oanda.cfg')

    def test_connection(self):
        self.assertIsNotNone(self.tpqoa.account_id)
        self.assertIsNotNone(self.tpqoa.access_token)

    def test_place_order(self):
        oanda_response = self.tpqoa.create_order('EUR_USD', units=10, ret=True)
        oanda_response = oanda_response.get('orderFillTransaction').dict()
        self.assertEqual(
            Decimal(oanda_response['units']), 10,
            'Open Order placed successfully')
        self.assertEqual(Decimal(
            oanda_response['tradeOpened']['units']), 10,
            'New trade opened check success')

        oanda_response = self.tpqoa.create_order(
            'EUR_USD', units=-10, ret=True)
        oanda_response = oanda_response.get('orderFillTransaction').dict()
        self.assertEqual(
            Decimal(oanda_response['units']), -10,
            'Close Order placed successfully')
        self.assertEqual(Decimal(
            oanda_response['tradesClosed'][0]['units']), -10,
            'Trade closed check success')

    def test_sl_distance(self):
        oanda_response = self.tpqoa.create_order(
            'EUR_USD', units=10, sl_distance=0.005, ret=True)
        oanda_response = oanda_response.get('orderCreateTransaction').dict()
        self.assertEqual(
            Decimal(oanda_response['stopLossOnFill']['distance']),
            round(Decimal(0.005), 3),
            'sl created successfully')

        oanda_response = self.tpqoa.create_order(
            'EUR_USD', units=-10, ret=True)

    def test_tsl_tp_order(self):
        oanda_response = self.tpqoa.create_order(
            'EUR_USD', units=10, sl_distance=0.0005, ret=True)
        oanda_create_response = oanda_response.get(
            'orderCreateTransaction').dict()
        self.assertEqual(
            Decimal(oanda_create_response['stopLossOnFill']['distance']),
            round(Decimal(0.0005), 4),
            'sl created successfully')
        trade_response = oanda_response.get('orderFillTransaction').dict()
        tp_price = float(trade_response['price']) + 0.001

        sleep(3)
        oanda_response = self.tpqoa.create_order(
            'EUR_USD', units=10, tsl_distance=0.0005,
            tp_price=tp_price, ret=True)
        oanda_create_response = oanda_response.get(
            'orderCreateTransaction').dict()
        self.assertEqual(
            Decimal(
                oanda_create_response['trailingStopLossOnFill']['distance']),
            round(Decimal(0.0005), 4), 'TSL created successfully')
        self.assertIsNotNone(
            round(
                Decimal(oanda_create_response['takeProfitOnFill']['price']), 4),
            'TP created successfully')

        sleep(3)
        oanda_response = self.tpqoa.create_order(
            'EUR_USD', units=-20, ret=True)

    def test_get_instruments(self):
        instruments = self.tpqoa.get_instruments()
        self.assertIsNotNone(instruments)
        eur_usd = [x for x in instruments if x[0] == 'EUR/USD']
        self.assertEqual(eur_usd, [('EUR/USD', 'EUR_USD')])


if __name__ == '__main__':
    unittest.main()
