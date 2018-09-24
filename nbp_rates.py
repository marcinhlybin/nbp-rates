#!/usr/bin/env python3
# Retrieves National Bank of Poland (NBP) currency rates

import os
import re
import csv
import time
import argparse
import requests
import itertools
from datetime import datetime, timedelta

CACHE_FILE = '/tmp/nbp_rates_{year}.csv'


def nbp_rate_last(currency, dt=datetime.utcnow()):
    """Returns NBP currency rate for last workday

    Arguments:
    dt       -- date as datetime object
    currency -- 3-letter currency symbol, e.g. EUR

    Return a tuple (date, price)
    """

    for i in range(1,10):
        lastday = dt - timedelta(days=i)
        rates = __init_rates(lastday)
        try:
            date = lastday.strftime('%Y%m%d')
            return date, rates[currency][date]
        except KeyError:
            continue


def nbp_rate(currency, dt=datetime.utcnow()):
    """Returns NBP currency rate for date

    Arguments:
    dt       -- date as datetime object
    currency -- 3-letter currency symbol, e.g. EUR
    """

    rates = __init_rates(dt)
    date = dt.strftime('%Y%m%d')
    try:
        return date, rates[currency][date]
    except KeyError as e:
        raise KeyError('NBP rate not found for date {}'.format(date)) from e


def nbp_rates(currency, year):
    """Returns yearly rates for a currency

    Arguments:
    year     -- year string, e.g. 2018
    currency -- 3-letter currency symbol, e.g. EUR
    """

    dt = datetime.strptime(str(year), '%Y')
    rates = __init_rates(dt)
    for date in sorted(rates[currency]):
        yield (date, rates[currency][date])


def __init_rates(dt):
    year = int(dt.strftime('%Y'))
    current_year = int(dt.utcnow().strftime('%Y'))
    if year < 2002 or year > current_year:
        raise ValueError('Rates not found for year {}'.format(year))

    __download_rates(year)

    cache_file = CACHE_FILE.format(year=year)
    with open(cache_file, encoding='iso8859-2') as f:
        data = csv.reader(f, delimiter=';')
        return __parse_rates(data)


def __download_rates(year):
    nbp_url = 'https://www.nbp.pl/kursy/Archiwum/archiwum_tab_a_{year}.csv'.format(year=year)
    cache_file = CACHE_FILE.format(year=year)

    if os.path.exists(cache_file):
        curtime = int(datetime.utcnow().strftime('%s'))
        mtime = int(os.path.getmtime(cache_file))
        if curtime - mtime <= 3600:
            return

    r = requests.get(nbp_url)
    with open(cache_file, 'wb') as f:
        f.write(r.content)

def __parse_rates(data):
    rates = {}
    currencies = []
    for row in data:
        # Get currencies names
        if not currencies:
            for field in row:
                currency_match = re.match('^\d+(\w+)$', field)
                if currency_match:
                    currency = currency_match[1]
                    rates[currency] = {}
                    currencies.append(currency)
            continue

        if not row:
            break

        # Get currency price by date
        date = row[0]
        date_match = re.match('^\d{8}$', date)
        if date_match:
            for i, currency in enumerate(currencies, 1):
                price = float(row[i].replace(',', '.'))
                rates[currency][date] = price

    return rates

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-y', '--year', metavar='YEAR', action='store', default=datetime.utcnow().strftime('%Y'))
    parser.add_argument('currency', metavar='CURRENCY', type=str)
    args = parser.parse_args()

    for date, price in nbp_rates(args.currency, args.year):
        print("{date}\t{price}".format(date=date, price=price))
