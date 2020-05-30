#!/usr/bin/env python3
# Retrieves National Bank of Poland (NBP) currency rates

import os
import re
import csv
import argparse
import requests
from datetime import datetime, timedelta

CACHE_FILE = '/tmp/nbp_rates_{type}_{year}.csv'
RATES = {}


def nbp_rate_last(currency, dt=datetime.utcnow()):
    """Returns NBP currency rate for last workday

        Arguments:
        dt       -- date as datetime object
        currency -- 3-letter currency symbol, e.g. EUR

        Returns a tuple (date, price)
    """

    currency = currency.upper()

    for i in range(10):
        lastday = dt - timedelta(days=i)
        year = int(lastday.strftime('%Y'))
        __init_rates(year)
        try:
            date = lastday.strftime('%Y%m%d')
            return date, RATES[year][currency][date]
        except KeyError:
            if i < 9: continue
            raise

def nbp_rate(currency, dt=datetime.utcnow()):
    """Returns NBP currency rate for date

    Arguments:
    dt       -- date as datetime object
    currency -- 3-letter currency symbol, e.g. EUR

    Returns a tuple (date, price)
    """

    currency = currency.upper()
    year = int(dt.strftime('%Y'))
    __init_rates(year)

    try:
        date = dt.strftime('%Y%m%d')
        return date, RATES[year][currency][date]
    except KeyError as e:
        raise KeyError('NBP rate not found for date {}'.format(date)) from e


def nbp_rates(currency, year):
    """Returns yearly rates for a currency

    Arguments:
    year     -- year string, e.g. 2018
    currency -- 3-letter currency symbol, e.g. EUR

    Returns a generator of tuples (date, price)
    """

    currency = currency.upper()
    year = int(year)
    __init_rates(year)
    for date in sorted(RATES[year][currency]):
        yield (date, RATES[year][currency][date])


def __init_rates(year):
    current_year = int(datetime.utcnow().strftime('%Y'))
    if year < 2002 or year > current_year:
        raise ValueError('Rates not found for year {}'.format(year))

    if year in RATES:
        return

    for rates_type in ('a', 'b'):
        __download_rates(year, rates_type)
        cache_file = CACHE_FILE.format(type=rates_type, year=year)
        with open(cache_file, encoding='iso8859-2') as f:
            data = csv.reader(f, delimiter=';')
            if year not in RATES:
                RATES[year] = {}
            RATES[year].update(__parse_rates(data))


def __download_rates(year, rates_type):
    nbp_url = 'https://www.nbp.pl/kursy/Archiwum/archiwum_tab_{type}_{year}.csv'.format(
      type=rates_type,
      year=year
    )
    cache_file = CACHE_FILE.format(type=rates_type, year=year)

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
                price = row[i].replace(',', '.')
                if not price:
                    continue
                rates[currency][date] = float(price)

    return rates

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-y', '--year', metavar='YEAR', action='store')
    parser.add_argument('currency', metavar='CURRENCY', type=str)
    args = parser.parse_args()

    if not args.year:
        date, price = nbp_rate_last(args.currency)
        print("{date}\t{price}".format(date=date, price=price))
    else:
        for date, price in nbp_rates(args.currency, args.year):
            print("{date}\t{price}".format(date=date, price=price))
