# Rebalance Calculator

Simple portfolio rebalance calculator.

Link: [Web App](https://kingle.pythonanywhere.com/rebalance)

[Changelog](https://github.com/kennguyen01/rebalance-calculator/releases)

## About

The aim of rebalancing is to control risk and diversify portfolio. This web app calculates the number of shares needed to be bought or sold to rebalance an investment portfolio. It uses [yfinance](https://github.com/ranaroussi/yfinance) to retrieves data from Yahoo Finance. It does not take into account security types that only allowed whole-share transaction such as ETF. 

## Run Locally

To run the app locally, install all dependencies and enter:

```console
$ export FLASK_APP=application.py FLASK_DEBUG=1
$ flask run
```

To run unit tests:

```console
python -m unittest discover
```
