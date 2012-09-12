#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import unittest
import logging

# Path hack.
sys.path.insert(0, os.path.abspath('..'))
import requests

rLog = logging.getLogger('requests')
rLog.setLevel(logging.WARNING)


class BasicTest(unittest.TestCase):
    """LxxL services basic test"""

    smoke_url = "http://localhost:8081/1.0/users/authenticate"

    def test_service_alive(self):
        result = requests.get(self.smoke_url)
        self.assertEqual(result.status_code, 401)

if __name__ == '__main__':
    unittest.main()
