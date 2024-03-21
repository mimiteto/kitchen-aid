#! /usr/bin/env python3

"""
Tests for the http requests wrapper
"""


import unittest

import httpx

from kitchen_aid.pkgs.http.http_requests import HTTPRequest


class TestHTTPRequest(unittest.TestCase):
    """ Test the HTTPRequest class """

    def test_do_request(self):
        """ Test the do_request method """
        request = HTTPRequest("http://example.com")
        response = request.do_request()
        self.assertIsInstance(response, httpx.Response)

    # pylint: disable=protected-access
    def test_init(self):
        """ Test the init method """
        request = HTTPRequest("http://example.com")
        self.assertEqual(request._url, "http://example.com")
        self.assertIsNone(request._headers)
        self.assertIsNone(request._params)
        self.assertEqual(request._timeout, 10)
        self.assertEqual(request._req_callable, httpx.get)
        self.assertIsNone(request._data)
        self.assertEqual(request._request_kw_args, {"timeout": 10})
        request = HTTPRequest(
            "http://example.com",
            method="POST",
            headers={"header": "value"},
            params={"param": "value"},
            data="data",
            timeout=5,
        )
        self.assertEqual(request._url, "http://example.com")
        self.assertEqual(request._headers, {"header": "value"})
        self.assertEqual(request._params, {"param": "value"})
        self.assertEqual(request._timeout, 5)
        self.assertEqual(request._req_callable, httpx.post)
        self.assertEqual(request._data, "data")
        self.assertEqual(
            request._request_kw_args,
            {
                "params": {"param": "value"},
                "headers": {"header": "value"},
                "timeout": 5,
                "data": "data",
            },
        )
