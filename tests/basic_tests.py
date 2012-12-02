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
        """0. Ping services"""
        result = requests.get(self.ping_url)
        self.assertEqual(result.status_code, 401)

    def test_1create_app_key(self):
        """1. Sign Api key - good secret"""
        result = requests.post(self.admin_url, data={
            'keyid': 'TEST',
            'xxxadmin': True,
            'hosts': '*',
            'secret': 'TEST'
        })
        self.assertIn(result.status_code, [201, 403])

    def test_2bad_sign_api_key(self):
        """2. Sign Api key - bad secret"""
        try:
            api = Lxxl('TEST', 'TEST2', host=self.api_url)
            res = api.users.authenticate()
        except exceptions.HTTPRequestException as e:
            self.assertEqual(e.response.json['code'], '10')

    def test_3good_sign_api_key(self):
        """3. Authentication Anonymous - bad password"""
        try:
            api = Lxxl('TEST', 'TEST', host=self.api_url)
            res = api.users.authenticate()
        except exceptions.HTTPRequestException as e:
            self.assertEqual(e.response.json['code'], '20')

    def test_4log_anonymous(self):
        """4. Authentication Anonymous - good password"""
        try:
            api = Lxxl('TEST', 'TEST', host=self.api_url)
            api.setCredentials('anonymous', '860b9dbbda6ee5f71ddf3b44e54c469e')
            api.users.create()
        except exceptions.HTTPRequestException as e:
            self.assertEqual(e.response.status_code, 400)

    def test_5_create_account(self):
        """5. Create Account"""
        try:
            api = Lxxl('TEST', 'TEST', host=self.api_url)
            api.setCredentials('anonymous', '860b9dbbda6ee5f71ddf3b44e54c469e')
            resp = api.users.create(
                username="toto42",
                password="toto42",
                email="void@webitup.fr"
            )
        except exceptions.HTTPRequestException as e:
            if not 'duplicate' in e.response.json['error']:
                raise Exception(e.response.json)

        activation = resp['message']

        try:
            resp = api.users.validate(email="void@webitup.fr", code=activation)
        except exceptions.HTTPRequestException as e:
            raise Exception(e.response)

    def test_6_log_user(self):
        """6. Login with the new user"""
        try:
            api = Lxxl('TEST', 'TEST', host=self.api_url)
            api.setCredentials('void@webitup.fr', 'toto42')
            resp = api.users.authenticate(forcepost=True)
        except exceptions.HTTPRequestException as e:
            raise Exception(e.response.json)


if __name__ == '__main__':
    unittest.main()
