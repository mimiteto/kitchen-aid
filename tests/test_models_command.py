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


class TestCommandHandlerExecute(unittest.TestCase):
    """ Tests for the execute method of the CommandHandler class """

    @patch('kitchen_aid.models.command.CommandMapper')
    def test_execute_success(self, mock_cmap):
        """ Test execute method when command succeeds """

        cmd_mock = MagicMock()
        cmd_instance_mock = MagicMock()
        cmd_instance_mock.execute.return_value = Result(
            success=True, message="Command executed successfully", errors=[]
        )
        cmd_mock.return_value = cmd_instance_mock
        cmap_obj = MagicMock()
        cmap_obj.get_command.return_value = (cmd_mock, MagicMock(), MagicMock())
        mock_cmap.return_value = cmap_obj

        ch = CommandHandler('test', None, None)
        result = ch.execute()

        self.assertTrue(result.success)
        self.assertEqual(result.message, "Command executed successfully")
        self.assertEqual(result.errors, [])

    @patch('kitchen_aid.models.command.CommandMapper')
    def test_execute_retry_limit_exceeded(self, mock_cmap):
        """ Test execute method when retry limit is exceeded """

        cmd_mock = MagicMock()
        cmd_instance_mock = MagicMock()
        cmd_instance_mock.execute.side_effect = RetriableError("Temporary error")
        cmd_mock.return_value = cmd_instance_mock
        cmap_obj = MagicMock()
        cmap_obj.get_command.return_value = (cmd_mock, MagicMock(), MagicMock())
        mock_cmap.return_value = cmap_obj

        ch = CommandHandler('test', None, None, retry_limit=2)

        with self.assertRaises(FailedOperation) as context:
            ch.execute()

        self.assertIn("Operation failed execution after 2 retries", str(context.exception))

    @patch('kitchen_aid.models.command.CommandMapper')
    def test_execute_failure(self, mock_cmap):
        """ Test execute method when command fails """

        cmd_mock = MagicMock()
        cmd_instance_mock = MagicMock()
        cmd_instance_mock.execute.side_effect = FailedOperation("Command failed")
        cmd_mock.return_value = cmd_instance_mock
        cmap_obj = MagicMock()
        cmap_obj.get_command.return_value = (cmd_mock, MagicMock(), MagicMock())
        mock_cmap.return_value = cmap_obj

        ch = CommandHandler('test', None, None)

        with self.assertRaises(FailedOperation) as context:
            ch.execute()

        self.assertIn("Operation failed after 3 retries", str(context.exception))

    @patch('kitchen_aid.models.command.CommandMapper')
    def test_execute_with_undo_success(self, mock_cmap):
        """ Test execute method when command succeeds and can undo """
        cmd_mock = MagicMock()
        cmd_instance_mock = MagicMock()
        cmd_instance_mock.execute.return_value = Result(success=True, message="Command executed successfully", errors=[])
        cmd_instance_mock.can_undo = True
        cmd_mock.return_value = cmd_instance_mock
        cmap_obj = MagicMock()
        cmap_obj.get_command.return_value = (cmd_mock, MagicMock(), MagicMock())
        mock_cmap.return_value = cmap_obj

        ch = CommandHandler('test', None, None)
        result = ch.execute()

        self.assertTrue(result.success)
        self.assertEqual(result.message, "Command executed successfully")
        self.assertEqual(result.errors, [])

    @patch('kitchen_aid.models.command.CommandMapper')
    def test_execute_with_undo_failure(self, mock_cmap):
        """ Test execute method when command fails and can undo """
        cmd_mock = MagicMock()
        cmd_instance_mock = MagicMock()
        cmd_instance_mock.execute.side_effect = FailedOperation("Command failed")
        cmd_instance_mock.can_undo = True
        cmd_mock.return_value = cmd_instance_mock
        cmap_obj = MagicMock()
        cmap_obj.get_command.return_value = (cmd_mock, MagicMock(), MagicMock())
        mock_cmap.return_value = cmap_obj

        ch = CommandHandler('test', None, None)

        with self.assertRaises(FailedOperation) as context:
            ch.execute()

        self.assertIn("Operation failed after 3 retries", str(context.exception))
