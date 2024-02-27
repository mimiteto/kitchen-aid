#! /usr/bin/env python3

"""
This module povides base interact utilities
"""


from typing import Any, OrderedDict
from queue import Queue
from threading import Lock

from gears.singleton_meta import SingletonController

import kitchen_aid.models.exceptions as excs
from kitchen_aid.models.command import Result, CommandMapper


def get_cmd_id(
        cmd: str,
        args: list[str],
        kw_args: dict[str, str],
        thread: "IThread",
        iface: "InteractInterface"
) -> str:
    """ Get a command id """
    cmd_id: str = f"cmd:{cmd};args:"
    cmd_id += ",".join(f"arg::{arg}" for arg in args)
    cmd_id += ";kw_args:"
    cmd_id += ",".join(f"kw_arg::{k}--{v}" for k, v in kw_args.items())
    cmd_id += f";thread:{thread};iface:{iface}"
    return cmd_id


def wrap_result(result: Result, call: str, filtered_args: list | None = None) -> str:
    """ Wrap the result to be human readable """
    msg = f"{call}"
    if filtered_args:
        msg += f" with args {filtered_args}"
    if result.success:
        msg += f" succeeded with message: {result.message}"
        if result.errors:
            msg += f" but had the following errors: {result.errors}"
    else:
        msg += f" failed with message: {result.message}"
        if result.errors:
            msg += f" and had the following errors: {result.errors}"
    return msg


# pylint: disable=too-few-public-methods
class IThread:  # pragma: no cover
    """
    Basic thread wrapper.
    Intention with thread is that it provides somewhat of universal way
    between interfaces to communicate.
    """

    def post(self, message: bytes | Any) -> None:
        """
        Post a message to the thread
        """
        raise NotImplementedError


class InteractInterface:
    """ Base interact interface """

    has_threads: bool = False

    def __init__(self, command_queue: Queue, command_result_queue: Queue) -> None:
        self.main_thread: IThread = self.get_main_thread()
        self._command_queue: Queue = command_queue
        self._command_result_queue: Queue = command_result_queue
        self._command_inventory: dict[str, Any] = {}
        self._lock: Lock = Lock()

    def listen(self) -> None:
        """
        Listen for inputs in this method.
        This method should go into infinite loop and listen for inputs.
        Take care of your inputs here as well.
        """
        raise NotImplementedError

    def get_main_thread(self) -> IThread:
        """ Get the main thread """
        raise NotImplementedError

    def _post_message(self, message: bytes, thread: IThread) -> None:
        """ Post a message """
        raise NotImplementedError

    def spawn_thread(self) -> IThread:
        """ Spawn a new thread """
        raise NotImplementedError

    def post(self, message: bytes) -> None:
        """ Post a message """
        self._post_message(
            message,
            self.spawn_thread() if self.has_threads else self.main_thread
        )

    # pylint: disable=too-many-arguments
    def receive_command(
        self,
        command: str,
        args: list | None = None,
        kwargs: dict | None = None,
        thread: IThread | None = None,
        cback_iiface: str | type["InteractInterface"] | None = None
    ) -> None:
        """ Receive a command and schedule it for execution """
        cback: InteractInterface
        args = args or []
        kwargs = kwargs or {}
        thread = thread or self.main_thread
        if cback_iiface is None:
            cback = self
        else:
            cback = InteractInterfacesRegistry().get(cback_iiface)  # type: ignore
        cmd_tuple: tuple[str, list[str], dict[str, str], IThread, InteractInterface] = (
            command, args, kwargs, thread, cback
        )
        do_put: bool = False
        cmd_id: str = get_cmd_id(command, args, kwargs, thread, cback)
        with self._lock:
            # Make sure that we don't shedule a command that is already scheduled
            if cmd_id not in self._command_inventory:
                self._command_inventory[cmd_id] = cmd_tuple
                do_put = True
        if do_put:
            self._command_queue.put(cmd_tuple)

    def post_command_result(
        self, cmd_id: str, result: Result
    ) -> None:
        """ Post a command result to the queue """
        cmd, args, kwargs, thread, _ = self._command_inventory[cmd_id]
        args.extend(f"{arg[0]}: {arg[1]}" for arg in kwargs.items())
        self._post_message(
            wrap_result(result, cmd, args).encode("utf-8"),
            thread
        )
        with self._lock:
            del self._command_inventory[cmd_id]


# Let's define a simple interface and threads that go with it.
# This will help for testing purposes.
# We wil ldefine this as the default iface as well.
class STDOutThread(IThread):
    """ Standard output thread """

    def post(self, message: bytes | Any) -> None:
        """ Post a message """
        print(message.decode("utf-8"))


class ClearTextInterface(InteractInterface):
    """ Command line interface """
    has_threads: bool = False

    def __init__(self, command_queue: Queue, command_result_queue: Queue) -> None:
        super().__init__(command_queue, command_result_queue)
        self._cmd_map = CommandMapper()

    def get_main_thread(self) -> IThread:
        """ Get the main thread """
        return STDOutThread()

    def _post_message(self, message: bytes, thread: IThread) -> None:
        """ Post a message """
        thread.post(message)

    def spawn_thread(self) -> IThread:
        """ Spawn a new thread """
        return self.main_thread

    def listen(self) -> None:
        """ Listen for inputs """
        stdin_input: str = ""
        while True:
            try:
                stdin_input = input("Enter command: ")
            except EOFError:
                print()
            if len(stdin_input) == 0:
                print("No command entered")
                continue
            cmd, *args = stdin_input.split()
            try:
                _, _, parser = self._cmd_map.get_command(cmd)  # type: ignore
            except excs.CommandNotFound:
                print(f"Command {cmd} not found")
                continue
            kw_args = vars(parser.parse_args(args))
            self.receive_command(
                command=cmd,
                args=[],
                kwargs=kw_args,
                thread=self.main_thread,
                cback_iiface=None
            )


class InteractInterfacesRegistry(metaclass=SingletonController):
    """ Singleton interact interface """

    def __init__(self) -> None:
        self._interfaces: OrderedDict[str, InteractInterface] = OrderedDict({})
        self._lock: Lock = Lock()
        self._command_queue: Queue
        self._command_result_queue: Queue
        self._default_class: type[InteractInterface] = ClearTextInterface

    @ property
    def default(self) -> InteractInterface:
        """ Get the default interface """
        self._register_default()
        return self._interfaces["default"]

    @ property
    def default_class(self) -> type[InteractInterface]:
        """ Get the default class """
        return self._default_class

    def add_queues(self, command_queue: Queue, command_result_queue: Queue) -> None:
        """ Add queues to the registry """
        self._command_queue = command_queue
        self._command_result_queue = command_result_queue
        self._register_default()

    def _register_default(self) -> None:
        """ Register the default interface """
        if self._command_queue is None or self._command_result_queue is None:
            raise RuntimeError("Queues not set!")

        if "default" not in self._interfaces:
            self._interfaces["default"] = self.default_class(
                self._command_queue, self._command_result_queue
            )

    def register(
        self,
        iface: InteractInterface,
        name: str | None = None
    ) -> None:
        """ Register an interface """
        self._register_default()
        name = name or iface.__class__.__name__
        with self._lock:
            self._interfaces[name] = iface

    def get(
        self, iface: str | type[InteractInterface] | None
    ) -> InteractInterface:
        """ Get an interface """
        self._register_default()
        if iface is None:
            return self._interfaces["default"]
        if isinstance(iface, type):
            with self._lock:
                for _, iface_type in self._interfaces.items():
                    if isinstance(iface_type, iface):
                        return iface_type
            return self._interfaces["default"]
        with self._lock:
            return self._interfaces[iface]
