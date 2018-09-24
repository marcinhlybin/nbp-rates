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

20180102	4.1701
20180103	4.1673
20180104	4.1515
20180105	4.1544
20180108	4.1647
20180109	4.1779
20180110	4.1784
20180111	4.1758
20180112	4.1669
20180115	4.1696
20180116	4.1825
20180117	4.1739
20180118	4.1663
[...]
```
