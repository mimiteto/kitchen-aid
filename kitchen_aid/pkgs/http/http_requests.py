#! /usr/bin/env python3

"""
Module provides http requests utils
"""

from typing import Any, Callable

import requests


# pylint: disable=too-few-public-methods
class HTTPRequest:
    """ Class to provide a basic HTTP request, definition detached from execution """

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        url: str,
        method: str = "GET",
        headers: dict[str, str] | None = None,
        params: dict[str, str] | None = None,
        data: str | None = None,
        timeout: int = 10,
    ) -> None:
        self._url: str = url
        self._headers: dict[str, str] | None = headers
        self._params: dict[str, str] | None = params
        self._timeout: int = timeout
        self._req_callable: Callable = getattr(requests, method.lower())
        self._data: str | None = data

        self._request_kw_args: dict[str, Any] = {}
        for key in ["params", "headers", "timeout", "data"]:
            if getattr(self, f"_{key}"):
                self._request_kw_args[key] = getattr(self, f"_{key}")

    def do_request(self) -> requests.Response:
        """ Get the web page """
        response: requests.Response = self._req_callable(self._url, **self._request_kw_args)
        response.raise_for_status()
        return response
