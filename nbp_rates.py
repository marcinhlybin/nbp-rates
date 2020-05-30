#!/usr/bin/env python3
# Retrieves National Bank of Poland (NBP) currency rates

import os
import re
import csv
import argparse
import requests
from datetime import datetime, timedelta
from dataclasses import dataclass

__all__ = [ 'nbp_rate_last', 'nbp_rate', 'nbp_rates' ]

DATA = {}
DATA_FILE = '/tmp/nbp_rates_{type}_{year}.csv'


def nbp_rate_last(symbol, dt=datetime.utcnow()):
    """Returns NBP symbol rate for last workday

        Arguments:
        dt       -- date as datetime object
        symbol -- 3-letter currency symbol, e.g. EUR

        Returns a tuple (date, price)
    """

    symbol = symbol.upper()

    for i in range(10):
        lastday = dt - timedelta(days=i)
        year = int(lastday.strftime('%Y'))
        init_rates(year)
        try:
            date = lastday.strftime('%Y%m%d')
            price = DATA[year][symbol][date]
            return date, price
        except KeyError:
            if i < 9: continue
            raise


def nbp_rate(symbol, dt=datetime.utcnow()):
    """Returns NBP symbol rate for date

    Arguments:
    dt       -- date as datetime object
    symbol -- 3-letter currency symbol, e.g. EUR

    Returns a tuple (date, price)
    """

    symbol = symbol.upper()
    year = int(dt.strftime('%Y'))
    init_rates(year)

    try:
        date = dt.strftime('%Y%m%d')
        price = DATA[year][symbol][date]
        return date, price
    except KeyError as e:
        raise KeyError('NBP rate not found for date {}'.format(date)) from e


def nbp_rates(symbol, year):
    """Returns yearly rates for a currency

    Arguments:
    year     -- year string, e.g. 2018
    symbol -- 3-letter currency symbol, e.g. EUR

    Returns a generator of tuples (date, price)
    """

    symbol = symbol.upper()
    year = int(year)
    init_rates(year)
    for date in sorted(DATA[year][symbol]):
        price = DATA[year][symbol][date]
        yield (date, price)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-y', '--year', metavar='YEAR', action='store')
    parser.add_argument('symbol', metavar='CURRENCY SYMBOL', type=str)
    args = parser.parse_args()

    if not args.year:
        date, price = nbp_rate_last(args.symbol)
        print("{date}\t{price}".format(date=date, price=price))
    else:
        for date, price in nbp_rates(args.symbol, args.year):
            print("{date}\t{price}".format(date=date, price=price))


#
# INTERNAL IMPLEMENTATION STARTS HERE
#
@dataclass
class Currency:
    name: str
    amount: int 


def init_rates(year):
    year = int(year)
    if not is_year_available(year):
        read_year_from_data_file(year)


def is_year_available(year):
    current_year = int(datetime.utcnow().strftime('%Y'))
    if year < 2002 or year > current_year:
        raise ValueError('Rates not found for year {}'.format(year))

    if year in DATA:
        return True


def read_year_from_data_file(year):
    for rates_type in ["a", "b"]:
        data_file = DATA_FILE.format(type=rates_type, year=year)
        
        if not data_file_is_fresh(data_file):
            download_rates_data(year, rates_type)
        
        with open(data_file, encoding='iso8859-2') as f:
            data = csv.reader(f, delimiter=';')
            get_year_from_data(year, data)


def get_year_from_data(year, data):
    if year not in DATA:
        DATA[year] = {}
    DATA[year].update(parse_rates_data(data))
    

def download_rates_data(year, rates_type):
    data_file = DATA_FILE.format(type=rates_type, year=year)
    download_url = "https://www.nbp.pl/kursy/Archiwum/archiwum_tab_{type}_{year}.csv".format(
      type=rates_type,
      year=year
    )
    r = requests.get(download_url)
    with open(data_file, 'wb') as f:
        f.write(r.content)


def data_file_is_fresh(data_file):
    if os.path.exists(data_file):
        curtime = int(datetime.utcnow().strftime('%s'))
        mtime = int(os.path.getmtime(data_file))
        if curtime - mtime <= 3600:
            return True


def parse_rates_data(data):
    rates = {}
    
    currency_row = next(data)
    currencies = list(get_currencies(currency_row))
    
    for row in data:
        if not row:
            continue

        date = row[0]
        if not is_date(date):
            continue

        # Get currency price by date
        for i, currency in enumerate(currencies, 1):
            price = row[i].replace(',', '.') 
            if not price:
                continue
            if currency.name not in rates:
                rates[currency.name] = {}
            rates[currency.name][date] = float(price)
            currency.price = 0

    return rates


def is_date(string):
    return re.match('^\d{8}$', string)


def is_currency_row(row):
    if len(row) > 0:
        return row[0] == "data"


def get_currencies(row):
    if not is_currency_row(row):
        raise ValueError("Currency row not found in data")
    
    for col in row:
        currency_match = re.match('^(\d+)(\w+)$', col)
        if currency_match:
            yield Currency(name=currency_match[2], amount=currency_match[1])


