# National Polish Bank (NBP) currency rates meet Python

## Usage

```
from nbp_rates import nbp_rate, nbp_rate_last
from datetime import datetime

currency = 'EUR'
dt = datetime.strptime('20180502', '%Y%m%d')

# Get NBP rate for date, raises KeyError if not found
nbp_rate(currency, dt) # ('20180502', 4.2675)

# Get NBP rate for last workday
nbp_rate_last(currency, dt) # ('20180430', 4.2204)
```

## CLI usage

```
usage: nbp_rates.py [-h] [-y YEAR] CURRENCY

positional arguments:
  CURRENCY

optional arguments:
  -h, --help            show this help message and exit
  -y YEAR, --year YEAR
```

Displays yearly rates for currency

```
$ nbp_rates.py -y 2018 EUR

20180102	3.4546
20180103	3.4616
20180104	3.4472
20180105	3.4488
20180108	3.4735
20180109	3.4992
20180110	3.4999
20180111	3.495
20180112	3.4366
20180115	3.401
20180116	3.419
20180117	3.4109
20180118	3.4108
[...]
```
