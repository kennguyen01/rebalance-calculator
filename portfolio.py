#!/usr/bin/env python3

import re
import yfinance as yf


class Portfolio:
    """Representation of user's portfolio"""

    def __init__(self):
        self.portfolio = []
        self.total = 0
        self.invalid = []

    def build_portfolio(self, tickers):
        """
        tickers: string of tickers
        Appends a dict to portfolio for each ticker in list
        """

        def process_string(s):
            """
            Removes any characters not in alphabet and turns ticker uppercase
            """
            regex = re.compile("[^a-zA-Z ]")
            new_s = regex.sub("", s)
            return new_s.strip().upper()

        if not tickers:
            return

        tickers = [process_string(ticker) for ticker in tickers.split(",")]
        for ticker in tickers:
            if ticker:
                self.portfolio.append({"Ticker": ticker})

    def reset_portfolio(self):
        self.portfolio = []
        self.invalid = []

    def reset_total(self):
        self.total = 0

    def get_portfolio(self):
        return self.portfolio

    def get_invalid(self):
        return self.invalid

    def get_total(self):
        return self.total

    def access_ticker_data(self):
        """
        Retrieves data from yfinance and updates ticker dict
        Returns first invalid ticker
        """
        # yfinance data keys
        n = "shortName"
        t = "quoteType"
        p = "regularMarketPrice"

        for d in self.portfolio:
            ticker = d["Ticker"]
            info = yf.Ticker(ticker).info
            if not info:
                self.invalid.append(ticker)
                continue
            d.update({"Name": info[n], "Type": info[t], "Price": info[p]})

    def set_ticker_balance(self, balances):
        balances = [float(balance) for balance in balances]
        for i, d in enumerate(self.portfolio):
            d["Balance"] = round(balances[i], 2)

    def set_invalid(self, invalids):
        assert type(invalids) == list

        for invalid in invalids:
            self.invalid.append(invalid)

    def set_target_allocation(self, allocations):
        # Checks if total allocations adds up to 100%
        allocations = [float(allocation) for allocation in allocations]
        print(allocations)
        if sum(allocations) != 100.0:
            return False

        for i, d in enumerate(self.portfolio):
            d["Target"] = round(allocations[i] / 100, 4)
        return True

    def set_total_balance(self, contribution=0):
        """
        contribution: 0 <= int <= 7000
        Updates total balance with ticker balance and contribution
        """
        for d in self.portfolio:
            self.total += d["Balance"]
        self.total += float(contribution)
        self.total = round(self.total, 2)

    def set_current_allocation(self):
        for d in self.portfolio:
            current = d["Balance"] / self.total
            d["Current"] = round(current, 4)

    def set_balance_difference(self):
        for d in self.portfolio:
            allocation_difference = d["Target"] - d["Current"]
            balance_difference = allocation_difference * self.total
            d["BalanceDifference"] = round(balance_difference, 2)

    def set_shares_difference(self):
        for d in self.portfolio:
            shares_difference = d["BalanceDifference"] / d["Price"]
            d["SharesDifference"] = round(shares_difference, 2)

    def calculate_data(self):
        self.set_current_allocation()
        self.set_balance_difference()
        self.set_shares_difference()

    def rebalance(self):
        """
        Rebalances portfolio based on user's desired allocation
        """
        self.calculate_data()

        # Calculate new ticker balance by selling and buying whole shares
        for d in self.portfolio:
            new_balance = d["Balance"] + d["BalanceDifference"]
            new_allocation = new_balance / self.total
            d["NewBalance"] = round(new_balance, 2)
            d["NewAllocation"] = round(new_allocation, 4)
