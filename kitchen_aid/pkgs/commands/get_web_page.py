#! /usr/bin/env python3

"""
Class provides a basic command that reads a web page
"""

import requests

from kitchen_aid.models.command import Command, Result


class GetWebPage(Command):
    """
    Command to get a web page
    """

    def __init__(self, url: str) -> None:
        self.url = url

    def execute(self) -> Result:
        """
        Get the web page
        """
        try:
            response = requests.get(self.url)
            response.raise_for_status()
            return Result(True, response.text, [])
        except requests.RequestException as error:
            return Result(False, str(error), [error])


# TODO: Add executor util and try it out
