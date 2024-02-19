#! /usr/bin/env python3

"""
Class provides a basic command that reads a web page
"""

import requests

from kitchen_aid.models.command import (
    Command,
    Result,
    FailedOperation,
)

from kitchen_aid.pkgs.http.http_requests import HTTPRequest


class GetWebPage(Command):
    """
    Command to get a web page
    """

    can_undo: bool = False

    def __init__(self, receiver: HTTPRequest) -> None:
        super().__init__(receiver=receiver)

    def undo(self) -> Result:
        """ Undo command. It will fail as it's not supported """
        raise FailedOperation(
            "Undo not supported",
            undo_result=Result(False, "Undo not supported", [])
        )

    def redo(self) -> Result:
        """ Redo command. It will fail as it's not supported """
        raise FailedOperation(
            "Redo not supported",
            undo_result=Result(False, "Redo not supported", [])
        )

    def execute(self) -> Result:
        """ Get the web page """
        try:
            response: requests.Response = self._receiver.do_request()
            return Result(True, response.text, [])
        except requests.RequestException as error:
            return Result(False, str(error), [error])
