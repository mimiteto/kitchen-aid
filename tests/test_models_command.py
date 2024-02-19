#! /usr/bin/env python3

"""
This module provides base command and result utilities
"""

import unittest
from unittest.mock import MagicMock, patch

from kitchen_aid.models.command import (
    Command,
    FailedOperation,
    RetriableError,
    Result,
    CommandHandler,
    CommandMapper
)


class TestCommandMapper(unittest.TestCase):
    """ Tests for the CommandMapper singleton  """

    def test(self):
        """ Test the CommandMapper singleton """
        cmap = CommandMapper()
        cmd = MagicMock()
        receiver = MagicMock()
        arg_parser = MagicMock()
        cmap.register(  # type: ignore
            cmd,
            receiver,
            'test',
            arg_parser
        )
        self.assertEqual(
            cmap.get_command('test'),
            (
                cmd, receiver, arg_parser
            )
        )


class TestCommandHandler(unittest.TestCase):
    """ Tests for the CommandHandler class """

    # pylint: disable=arguments-differ
    @patch('kitchen_aid.models.command.CommandMapper')
    def test_init(self, mock_cmap):
        """ Test the default command handler """
        cmd = MagicMock()
        cmd_option = MagicMock()
        cmd.return_value = cmd_option
        receiver = MagicMock()
        arg_parser = MagicMock()
        cmap_obj = MagicMock()
        cmap_obj.get_command.return_value = (
            cmd,
            receiver,
            arg_parser
        )
        mock_cmap.return_value = cmap_obj

        ch = CommandHandler('test', None, None)
        self.assertEqual(ch.command, cmd_option)
        self.assertEqual(ch.retry_limit, 3)
