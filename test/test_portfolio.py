#!/usr/bin/env python3

import copy
import unittest

from portfolio import Portfolio


class TestNewPortfolio(unittest.TestCase):

    def setUp(self):
        self.p = Portfolio()

    def tearDown(self):
        del self.p

    def test_no_ticker(self):
        self.p.build_portfolio("")
        p = self.p.get_portfolio()
        self.assertEqual([], p)

    def test_one_ticker(self):
        t = [{"Ticker": "A"}]

        self.p.build_portfolio('a')
        p = self.p.get_portfolio()
        self.assertEqual(t, p)

    def test_multiple_tickers(self):
        t = [{'Ticker': 'A'}, {'Ticker': 'BC'}, {'Ticker': 'DEF'}]

        self.p.build_portfolio("a, bc, def")
        p = self.p.get_portfolio()
        self.assertEqual(t, p)

    def test_random_symbols(self):
        self.p.build_portfolio("!\"#$%&'()*+,-./:;<=>?@[\]^_`{|}~")
        p = self.p.get_portfolio()
        self.assertEqual([], p)

    def test_combinations(self):
        t = [{'Ticker': 'ABC'}, {'Ticker': 'XYZ'}]

        self.p.build_portfolio('abc, xyz, ;<=>?@')
        p = self.p.get_portfolio()
        self.assertEqual(t, p)


class TestPortfolioResets(unittest.TestCase):

    def setUp(self):
        self.p = Portfolio()

    def tearDown(self):
        pass

    def test_reset_portfolio(self):
        self.p.reset_portfolio()
        self.assertEqual(self.p.get_portfolio(), [], "Expected empty list")


class TestAccessTickerData(unittest.TestCase):

    def setUp(self):
        self.p = Portfolio()

    def test_invalid_ticker(self):
        self.p.build_portfolio("zzzzz")
        self.p.access_ticker_data()
        invalid = ["ZZZZZ"]
        self.assertEqual(self.p.get_invalid(), invalid, "Expected empty list")

    def test_correct_tickers(self):
        self.p.build_portfolio("amzn, spy, vtsmx")
        expected_keys = ["Ticker", "Name", "Type", "Price"]
        self.p.access_ticker_data()
        for d in self.p.get_portfolio():
            k = list(d.keys())
            self.assertEqual(k, expected_keys, "Expected key not found")


class TestUserInputs(unittest.TestCase):

    def setUp(self):
        self.p = Portfolio()
        self.p.build_portfolio("amzn, spy, vtsmx")
        self.p.access_ticker_data()

    def test_ticker_balance(self):
        balances = ["2354.44", "633.89", "1539.44"]
        self.p.set_ticker_balance(balances)

        p = self.p.get_portfolio()
        for i, d in enumerate(p):
            self.assertEqual(d["Balance"], round(float(balances[i]), 2), "Incorrect ticker balance")

    def test_correct_target_allocation(self):
        allocations = ["55.25", "10", "34.75"]
        self.p.set_target_allocation(allocations)

        p = self.p.get_portfolio()
        for i, d in enumerate(p):
            self.assertEqual(d["Target"], round(float(allocations[i]) / 100, 4), "Incorrect target allocation")

    def test_incorrect_target_allocation(self):
        allocations_1 = ["1", "2", "3"]
        n = self.p.set_target_allocation(allocations_1)
        self.assertEqual(n, False, 'Expected False')

        allocations_2 = ["101", "102", "103"]
        m = self.p.set_target_allocation(allocations_2)
        self.assertEqual(m, False, 'Expected False')


class TestPortfolioCalculations(unittest.TestCase):

    def setUp(self):
        self.p = Portfolio()
        self.p.build_portfolio("dis, v, msft")
        self.p.access_ticker_data()

        balances = ["1620.82", "3156.32", "3753.47"]
        allocations = ["25", "45", "30"]

        self.p.set_ticker_balance(balances)
        self.p.set_target_allocation(allocations)
        self.p.set_total_balance()

        self.p.calculate_data()

    def test_calculate_total(self):
        total = 8530.61
        self.assertEqual(total, self.p.get_total(), 'Total balance incorrect')

    def test_calculate_current_allocations(self):
        current = [.19, .37, .44]
        for i, d in enumerate(self.p.get_portfolio()):
            self.assertEqual(d["Current"], current[i], 'Current allocation incorrect')

    def test_calculate_balance_difference(self):
        difference = [511.84, 682.45, -1194.29]
        for i, d in enumerate(self.p.get_portfolio()):
            self.assertEqual(d["BalanceDifference"], difference[i], 'Balance difference incorrect')


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
