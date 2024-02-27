#! /usr/bin/env python3

""" Tests for the interact module """

import unittest
from unittest.mock import MagicMock

from kitchen_aid.models.command import Result
from kitchen_aid.models.interact import (
    get_cmd_id,
    wrap_result,
    IThread,
    InteractInterface,
    # STDOutThread,
    # ClearTextInterface,
    # InteractInterfacesRegistry
)


class TestInteract(unittest.TestCase):
    """ Tests for the interact module """

    def test_wrap_result(self):
        """ Test wrap_result """
        with self.subTest("success"):
            result = Result(True, "success", [])
            call = "test"
            filtered_args = ["arg1", "arg2"]
            msg = wrap_result(result, call, filtered_args)
            self.assertEqual(
                msg,
                "test with args ['arg1', 'arg2'] succeeded with message: success"
            )
        with self.subTest("failure"):
            result = Result(False, "failure", ["error1", "error2"])
            call = "test"
            filtered_args = ["arg1", "arg2"]
            msg = wrap_result(result, call, filtered_args)
            # pylint: disable=line-too-long
            self.assertEqual(
                msg,
                "test with args ['arg1', 'arg2'] failed with message: failure and had the following errors: ['error1', 'error2']"
            )
        with self.subTest("success with errors"):
            result = Result(True, "success", ["errror", "errs"])
            call = "test"
            msg = wrap_result(result, call)
            # pylint: disable=line-too-long
            self.assertEqual(
                msg,
                "test succeeded with message: success but had the following errors: ['errror', 'errs']"
            )
        with self.subTest("no errors"):
            result = Result(False, "failure", [])
            call = "test"
            msg = wrap_result(result, call)
            self.assertEqual(
                msg,
                "test failed with message: failure"
            )

    def test_get_cmd_id(self):
        """ Test get_cmd_id """
        with self.subTest("All params"):
            # pylint: disable=line-too-long
            self.assertEqual(
                get_cmd_id(
                    "test",
                    ["arg1", "arg2"],
                    {"kw1": "arg1", "kw2": "arg2"},
                    "thread",  # type: ignore
                    "iface"  # type: ignore
                ),
                "cmd:test;args:arg::arg1,arg::arg2;kw_args:kw_arg::kw1--arg1,kw_arg::kw2--arg2;thread:thread;iface:iface",
            )

        with self.subTest("No args"):
            # pylint: disable=line-too-long
            self.assertEqual(
                get_cmd_id(
                    "test",
                    [],
                    {"kw1": "arg1", "kw2": "arg2"},
                    "thread",  # type: ignore
                    "iface"  # type: ignore
                ),
                "cmd:test;args:;kw_args:kw_arg::kw1--arg1,kw_arg::kw2--arg2;thread:thread;iface:iface",
            )


class TestInteractInterface(unittest.TestCase):
    """ Tests for InteractInterface """

    class FakeInteractInterface(InteractInterface):
        """ Fake InteractInterface """

        def spawn_thread(self) -> IThread:
            """ Spawn a thread """
            return MagicMock()

        def get_main_thread(self) -> IThread:
            """ Get main thread """
            return MagicMock()

        # pylint: disable=unused-argument
        def _post_message(self, message: bytes, thread: IThread) -> None:
            """ Post a message to the thread """

        def listen(self) -> None:
            """ Listen for messages """

    # pylint: disable=protected-access
    def test_init(self):
        """ Test __init__ """
        command_queue = MagicMock()
        command_result_queue = MagicMock()
        iface = self.FakeInteractInterface(command_queue, command_result_queue)
        self.assertEqual(iface._command_queue, command_queue)
        self.assertEqual(iface._command_result_queue, command_result_queue)
        self.assertEqual(iface._command_inventory, {})
