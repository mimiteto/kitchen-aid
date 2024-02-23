#! /usr/bin/env python3

"""
Tests for the get_web_page command
"""

import unittest

from unittest.mock import MagicMock

from requests.exceptions import RequestException

from kitchen_aid.models.command import FailedOperation, Result
from kitchen_aid.pkgs.commands.get_web_page import GetWebPage


class TestGetWebPage(unittest.TestCase):
    """ Test the get_web_page command """

    def test_redo_undo(self):
        """ Ensure redo/undo fail as commands """
        receiver = MagicMock()
        get_web_page = GetWebPage(receiver)
        with self.assertRaises(FailedOperation):
            get_web_page.redo()
        with self.assertRaises(FailedOperation):
            get_web_page.undo()

    def test_execute(self):
        """ Test the execute method """

        with self.subTest("Happy scenario"):
            receiver = MagicMock()
            receiver.do_request.return_value = MagicMock(text="Text")
            get_web_page = GetWebPage(receiver)
            result = get_web_page.execute()
            self.assertEqual(result, Result(True, "Text", []))

        with self.subTest("Sad scenario"):
            exc = RequestException("Error")
            receiver = MagicMock()
            receiver.do_request.side_effect = exc
            get_web_page = GetWebPage(receiver)
            result = get_web_page.execute()
            self.assertEqual(result.success, False)
            self.assertEqual(result.message, "Error")
            self.assertEqual(result.errors, [exc])
