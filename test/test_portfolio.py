#!/usr/bin/env python3

import copy
import csv
import random
import unittest

from portfolio import Portfolio

TICKERS = []
with open("s&p500.csv", "r") as f:
    reader = csv.reader(f)
    for row in reader:
        TICKERS.append(row[0])


def generate_tickers_string():
    """Returns a string containing n tickers where 1 <= n <= 10"""
    tickers = [random.choice(TICKERS) for _ in range(10)]
    return ", ".join(tickers)


def generate_portfolio_inputs(tickers):
    """
    tickers: list of ticker str
    Returns tuple of list for random balance and target allocation
    """
    allocations = []
    balances = []
    for i in range(len(tickers)):
        a = random.random()
        b = round(random.uniform(1.0, 10000.00), 2)
        allocations.append(a)
        balances.append(str(b))
    allocations = [round(i / sum(allocations) * 100, 4) for i in allocations]
    return allocations, balances


class TestNewPortfolio(unittest.TestCase):

    def setUp(self):
        self.p = Portfolio()

    def tearDown(self):
        del self.p

    def test_no_ticker(self):
        self.p.build_portfolio("")
        test = []
        result = self.p.get_portfolio()
        self.assertEqual(test, result)

    def test_one_ticker(self):
        test = [{"Ticker": "A"}]
        self.p.build_portfolio('a')

        result = self.p.get_portfolio()
        self.assertEqual(test, result)

    def test_multiple_tickers(self):
        test = [{'Ticker': 'A'}, {'Ticker': 'BC'}, {'Ticker': 'DEF'}]
        self.p.build_portfolio("a, bc, def")

        result = self.p.get_portfolio()
        self.assertEqual(test, result)

    def test_random_symbols(self):
        self.p.build_portfolio("!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~0123456789")

        test = []
        result = self.p.get_portfolio()
        self.assertEqual(test, result)

    def test_combinations(self):
        test = [{'Ticker': 'ABC'}, {'Ticker': 'XYZ'}]
        self.p.build_portfolio("abc, xyz, ;<=>?@, !@%, ^@#4590")

        result = self.p.get_portfolio()
        self.assertEqual(test, result)


class TestResetPortfolio(unittest.TestCase):

    def setUp(self):
        self.p = Portfolio()
        self.test = []

    def tearDown(self):
        del self.p

    def test_one_ticker(self):
        self.p.build_portfolio(random.choice(TICKERS))
        self.p.reset_portfolio()

        result = self.p.get_portfolio()
        self.assertEqual(self.test, result)

    def test_multiple_tickers(self):
        self.p.build_portfolio(generate_tickers_string())
        self.p.reset_portfolio()

        result = self.p.get_portfolio()
        self.assertEqual(self.test, result)

    def test_one_invalid(self):
        self.p.build_portfolio("eeeeee")
        self.p.set_ticker_data()
        self.p.reset_portfolio()

        result = self.p.get_portfolio()
        self.assertEqual(self.test, result)

    def test_multiple_invalids(self):
        self.p.build_portfolio("alsdrhgla, 027043o15h, !#%#$asdgfhjka")
        self.p.set_ticker_data()
        self.p.reset_portfolio()

        result = self.p.get_portfolio()
        self.assertEqual(self.test, result)


class TestAccessTickerData(unittest.TestCase):

    def setUp(self):
        self.p = Portfolio()

    def tearDown(self):
        del self.p

    def test_one_invalid(self):
        self.p.build_portfolio("zzzzz")
        self.p.set_ticker_data()

        test = ["ZZZZZ"]
        result = self.p.get_invalid()
        self.assertEqual(test, result)

    def test_multiple_invalids(self):
        self.p.build_portfolio("algaksd, !#%021348, lhganl")
        self.p.set_ticker_data()

        test = ['ALGAKSD', 'LHGANL']
        result = self.p.get_invalid()
        self.assertEqual(test, result)

    def test_expected_keys(self):
        self.p.build_portfolio(generate_tickers_string())
        self.p.set_ticker_data()

        test = ["Ticker", "Name", "Type", "Price"]
        self.p.set_ticker_data()
        for d in self.p.get_portfolio():
            result = list(d.keys())
            self.assertEqual(test, result)

    def test_one_ticker(self):
        self.p.build_portfolio("tsla")
        self.p.set_ticker_data()
        for d in self.p.get_portfolio():
            for k, v in d.items():
                self.assertIsNotNone(k)
                self.assertIsNotNone(v)

    def test_multiple_tickers(self):
        self.p.build_portfolio(generate_tickers_string())
        self.p.set_ticker_data()
        for d in self.p.get_portfolio():
            for k, v in d.items():
                self.assertIsNotNone(k)
                self.assertIsNotNone(v)


class TestUserInputs(unittest.TestCase):

    def setUp(self):
        self.p = Portfolio()
        self.p.build_portfolio("jnj, bac, baba")
        self.p.set_ticker_data()

    def tearDown(self):
        del self.p

    def test_ticker_balance(self):
        balances = ["2354.44", "633.89", "1539.44"]
        self.p.set_ticker_balance(balances)

        p = self.p.get_portfolio()
        for i, d in enumerate(p):
            test = round(float(balances[i]), 2)
            result = d["Balance"]
            self.assertEqual(test, result)

    def test_correct_target_allocation(self):
        allocations = ["55.25", "10", "34.75"]
        self.p.set_target_allocation(allocations)

        p = self.p.get_portfolio()
        for i, d in enumerate(p):
            test = round(float(allocations[i]) / 100, 4)
            result = d["Target"]
            self.assertEqual(test, result)

    def test_incorrect_target_allocation(self):
        allocations_1 = ["1", "2", "3"]
        result = self.p.set_target_allocation(allocations_1)
        self.assertFalse(result)

        allocations_2 = ["101", "102", "103"]
        result = self.p.set_target_allocation(allocations_2)
        self.assertFalse(result)


class TestPortfolioCalculations(unittest.TestCase):

    def setUp(self):
        self.p = Portfolio()
        self.p.build_portfolio("dis, v, msft, f")
        self.p.set_ticker_data()
        self.allocations, self.balances = generate_portfolio_inputs(self.p.get_portfolio())

        self.p.set_ticker_balance(self.balances)
        self.p.set_target_allocation(self.allocations)
        self.p.set_total_balance()
        self.p.calculate_data()

    def tearDown(self):
        del self.p
        del self.allocations
        del self.balances

    def test_calculate_total(self):
        test = sum([float(i) for i in self.balances])
        result = self.p.get_total()
        self.assertEqual(test, result)

    def test_calculate_current_allocations(self):
        for i, d in enumerate(self.p.get_portfolio()):
            test = round(d["Balance"] / self.p.get_total(), 4)
            result = d["Current"]
            self.assertEqual(test, result)

    def test_calculate_balance_difference(self):
        for i, d in enumerate(self.p.get_portfolio()):
            difference = d["Target"] - d["Current"]
            test = round(difference * self.p.get_total(), 2)
            result = d["BalanceDifference"]
            self.assertAlmostEqual(test, result)


class TestRebalance(unittest.TestCase):

    def setUp(self):
        self.p = Portfolio()
        self.p.build_portfolio("aapl, vti, axp, fssnx, ko")
        self.p.access_ticker_data()

        balances = ["3062.67", "5290.07", "7517.47", "3897.95", "8074.32"]
        allocations = ["15", "30", "15", "15", "25"]

        self.p.set_ticker_balance(balances)
        self.p.set_target_allocation(allocations)

    def test_rebalance_with_multiple_contributions(self):
        contributions = [n for n in range(0, 7001, 200)]
        for contribution in contributions:
            # Default portfolio before rebalance
            default = copy.deepcopy(self.p)
            with self.subTest(contribution=contribution):
                default.set_total_balance(contribution)
                default.rebalance()

            for d in default.get_portfolio():
                new_balance = d["Balance"] + d["BalanceDifference"]
                new_allocation = new_balance / default.get_total()
                self.assertEqual(d["NewBalance"], round(new_balance, 2), "New balance incorrect")
                self.assertEqual(d["NewAllocation"], round(new_allocation, 2), "New Allocation incorrect")


if __name__ == "__main__":
    unittest.main()
