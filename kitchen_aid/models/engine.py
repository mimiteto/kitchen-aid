#! /usr/bin/env python3

"""
This module povides the kitchen aid engine.
"""

from threading import Lock, Thread
from concurrent.futures import ThreadPoolExecutor, Executor, Future
from queue import Queue
from typing import Any, Callable
from time import sleep

from kitchen_aid.models.command import Result, CommandHandler
from kitchen_aid.models.interact import IThread, InteractInterface, InteractInterfacesRegistry


def get_cmd_id(
        cmd: str,
        args: list[str],
        kw_args: dict[str, str],
        thread: IThread,
        iface: InteractInterface
) -> str:
    """ Get a command id """
    cmd_id: str = f"cmd:{cmd},args:"
    for arg in args:
        cmd_id += f"arg::{arg}"
    cmd_id += ",kw_args:"
    for k, v in kw_args.items():
        cmd_id += f"kw_arg::{k}--{v}"
    cmd_id += f",thread:{thread},iface:{iface}"
    return cmd_id


class Engine:
    """ Base engine class """

    def __init__(self, max_workers: int | None = None) -> None:
        self._executor: Executor = ThreadPoolExecutor(max_workers)
        self._lock: Lock = Lock()

    def execute(self) -> None:
        """ Use this method to execute the engine logic"""
        raise NotImplementedError

    def run(self) -> None:
        """ Use this method to keep the engine running """
        raise NotImplementedError


class CommandEngine(Engine):
    """
    Command engine.
    This engine is dedicated to scheduling and execution of commands.
    """

    def __init__(self, max_workers: int | None = None) -> None:
        super().__init__(max_workers)
        self._command_result_queue: Queue = Queue()
        self._command_queue: Queue = Queue()

    @property
    def command_result_queue(self) -> Queue:
        """ Get the command result queue """
        return self._command_result_queue

    @property
    def command_queue(self) -> Queue:
        """ Get the command queue """
        return self._command_queue

    def _emmit_command_result(
        self, cmd_id: str, result: Result, iface: InteractInterface
    ) -> None:
        """ Emit command results over the result interface. """
        iface.post_command_result(cmd_id, result)

    def run(self) -> None:
        """ Run the engine """
        cmd_exec_thread = Thread(
            target=self.execute, daemon=True, name="cmd_exec_thread"
        )
        message_emmit_thread = Thread(
            target=self.emmit_command_results, daemon=True, name="message_emmit_thread"
        )

        cmd_exec_thread.start()
        message_emmit_thread.start()
        while True:
            sleep(1)  # There are no blocking steps here
            if not cmd_exec_thread.is_alive():
                cmd_exec_thread = Thread(
                    target=self.execute, daemon=True, name="cmd_exec_thread"
                )
                cmd_exec_thread.start()
            if not message_emmit_thread.is_alive():
                message_emmit_thread = Thread(
                    target=self.emmit_command_results, daemon=True, name="message_emmit_thread"
                )
                message_emmit_thread.start()

    def emmit_command_results(self) -> None:
        """
        Emit command results over the result interface.
        Emissions are threaded.
        Call this method in it's own thread.
        """
        while True:
            cmd_id, result, iface = self._command_result_queue.get()
            self._emmit_command_result(cmd_id, result, iface)

    def execute(self) -> None:
        """
        Execute polls the command queue and schedules the command for execution.
        Results are placed in the result queue.
        """

        while True:
            cmd, args, kw_args, thread, iface = self._command_queue.get()
            cmd_id = get_cmd_id(cmd, args, kw_args, thread, iface)
            cmd_handler = CommandHandler(
                command=cmd, args=args, kwargs=kw_args
            )
            future: Future = self._executor.submit(cmd_handler.command.execute)
            future.add_done_callback(
                lambda future: self._command_result_queue.put(
                    (cmd_id, future.result(), iface)
                )
            )


class InteractEngine(Engine):
    """
    Interact engine.
    This engine is dedicated to scheduling and execution of interactions.
    """

    def __init__(
        self, conf: dict[str, Any], command_queue: Queue, command_result_queue: Queue
    ) -> None:
        super().__init__()
        self._cmd_queue: Queue = command_queue
        self._result_queue: Queue = command_result_queue
        self._conf: dict[str, Any] = conf
        self._interact_confs: list[dict[str, Any]] = conf.get("interacts", [])
        self._reg: InteractInterfacesRegistry = InteractInterfacesRegistry()  # type: ignore
        self._reg.add_queues(self._cmd_queue, self._result_queue)  # type: ignore
        self._interact_listeners: list[str] = []

    def gen_interacts(self) -> None:
        """
        Generate interacts based on the configs.
        Interacts are added to the registry.
        If the interact conf has a key `start` with value `True` that interact
          is added to the list of interacts that will be started in listen mode
        """
        if not self._conf["interacts"]:
            self._reg.get(None)
            self._interact_listeners = ["default"]
            return

        for conf in self._interact_confs:
            do_start = conf.pop("start", False)
            name = conf.pop("name", None)
            iface_type = conf.pop("interface_type", self._reg.default_class)
            self._reg.register(iface_type(**conf), name)
            if do_start:
                self._interact_listeners.append(name)

    def run(self) -> None:
        """ Run the engine """
        interact_exec_thread = Thread(
            target=self.execute, daemon=True, name="interact_exec_thread"
        )
        interact_exec_thread.start()
        while True:
            sleep(1)
            if not interact_exec_thread.is_alive():
                interact_exec_thread = Thread(
                    target=self.execute, daemon=True, name="interact_exec_thread"
                )
                interact_exec_thread.start()

    def execute(self) -> None:
        """
        Method generates all interacts and starts listening
          on the ones that are set to start in separate threads.
        Method will restart failed threads.
        """
        self.gen_interacts()
        threads: dict[str, Thread] = {}

        def start_listener(iface: str) -> None:
            """ Start the listener in it's thread """
            interact = self._reg.get(iface)
            threads[iface] = Thread(target=interact.listen, daemon=True, name=iface)
            threads[iface].start()

        for iface in self._interact_listeners:
            start_listener(iface)
        while True:
            sleep(1)
            for iface in self._interact_listeners:
                if not threads[iface].is_alive():
                    start_listener(iface)
