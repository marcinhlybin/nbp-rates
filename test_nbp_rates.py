#!/usr/bin/env python3

import unittest
from datetime import datetime
from nbp_rates import nbp_rate, nbp_rate_last, nbp_rates

class UnitTests(unittest.TestCase):

    def test_nbp_rate(self):
        dt = datetime.strptime('2018-09-03', '%Y-%m-%d')
        self.assertEqual(nbp_rate('usd', dt), ('20180903', 3.6991))

    def test_nbp_rate_exc(self):
        dt = datetime.strptime('2018-01-01', '%Y-%m-%d')
        with self.assertRaises(KeyError):
            nbp_rate('eur', dt)

    def test_nbp_rate_last(self):
        dt = datetime.strptime('2018-01-01', '%Y-%m-%d')
        self.assertEqual(nbp_rate_last('cad', dt), ('20171229', 2.7765))

    def test_nbp_rate_last_now(self):
        dt = datetime.utcnow()
        self.assertIsInstance(nbp_rate_last('eur', dt)[1], float)

    def test_nbp_rate_last_tab_b(self):
        dt = datetime.strptime('2018-01-01', '%Y-%m-%d')
        self.assertEqual(nbp_rate_last('gel', dt), ('20171227', 1.3633))

    def test_nbp_rate_last_exc(self):
        dt = datetime.strptime('2001-10-01', '%Y-%m-%d')
        with self.assertRaises(ValueError):
            nbp_rate_last('THB', dt)

    def test_nbp_rates(self):
        self.assertEqual(len(list(nbp_rates('usd', 2017))), 251)

    def test_nbp_rate_tab_b(self):
        dt = datetime.strptime('2018-09-05', '%Y-%m-%d')
        self.assertEqual(nbp_rate('gel', dt), ('20180905', 1.4373))


if __name__ == '__main__':
    unittest.main()
