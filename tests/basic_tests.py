#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import unittest
import logging

# Path hack.
sys.path.insert(0, os.path.abspath('..'))
import requests
from lxxl.api import Lxxl, exceptions

rLog = logging.getLogger('requests')
rLog.setLevel(logging.WARNING)


class BasicTest(unittest.TestCase):
    """LxxL services basic test"""

    ping_url = "http://localhost:8081/1.0/users/authenticate"
    admin_url = "http://localhost:8084/1.0/key/"
    api_url = "localhost:8081"

    def test_0service_alive(self):
        result = requests.get(self.ping_url)
        self.assertEqual(result.status_code, 401)

    def test_1create_app_key(self):
        result = requests.post(self.admin_url, data={
            'keyid': 'TEST',
            'xxxadmin': True,
            'hosts': '*',
            'secret': 'TEST'
        })
        self.assertIn(result.status_code, [201, 403])

    def test_2bad_sign_api_key(self):
        try:
            api = Lxxl('TEST', 'TEST2', host=self.api_url)
            res = api.users.authenticate()
        except exceptions.HTTPRequestException as e:
            self.assertEqual(e.response.json['code'], '10')

    def test_3good_sign_api_key(self):
        try:
            api = Lxxl('TEST', 'TEST', host=self.api_url)
            res = api.users.authenticate()
        except exceptions.HTTPRequestException as e:
            self.assertEqual(e.response.json['code'], '20')

if __name__ == '__main__':
    unittest.main()
