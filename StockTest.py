#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from bot_gae import stock

class MyTestCase(unittest.TestCase):
    def test_stock(self):
        resp = stock('сапоги', 11)
        print resp
        self.assertEqual('Stock for 42 is 42', resp)


if __name__ == '__main__':
    unittest.main()
