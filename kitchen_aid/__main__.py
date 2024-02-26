#! /usr/bin/env python3

"""
Entrypoint for kitchen_aid package.
Use like:
    python3 -m kitchen_aid --config config
    OR
    python3 -m kitchen_aid --command command [with optional args]
"""

from time import sleep
import argparse
from sys import argv
from threading import Thread

from kitchen_aid.models.command import CommandMapper, CommandHandler
from kitchen_aid.models.engine import CommandEngine, InteractEngine

# commands
from kitchen_aid.pkgs.commands.get_web_page import (
    GetWebPage, HTTPRequest
)


def usage(args: list[str]) -> None:
    """ Print usage """
    print("Usage: python3 -m kitchen_aid --config config")
    print("OR")
    print("Usage: python3 -m kitchen_aid --command command [with optional args]")
    print("Command args are specific to the command")
    print(f"Called with args: {args}")


def register_commands() -> None:
    """ Register commands """

    def generate_parser(arguments: list[tuple[list, dict]]) -> argparse.ArgumentParser:
        """ Generate a parser from args"""
        parser = argparse.ArgumentParser()
        for args, kwargs in arguments:
            parser.add_argument(*args, **kwargs)
        return parser

    CommandMapper().register(
        GetWebPage,
        HTTPRequest,
        "get-page",
        generate_parser([
            (['url'], {"help": "URL to get"}),
            (
                ["-m", "--method"],
                {"help": "HTTP method", "default": "GET", "type": str}
            ),
            (
                ["--headers"],
                {"help": "HTTP headers", "type": dict[str, str], "default": {}}
            ),
            (
                ["-p", "--params"],
                {"help": "HTTP params", "type": dict[str, str], "default": {}}
            ),
            (
                ["-d", "--data"],
                {"help": "HTTP data", "type": str, "default": None},
            ),
            (
                ["-t", "--timeout"],
                {"help": "HTTP timeout", "type": int, "default": 10},
            ),
        ])
    )


def execute_command_flow(args: list[str]) -> None:
    """ Execute a command """
    command_name = args[0]
    _, _, parser = CommandMapper().get_command(command_name)
    kw_args = vars(parser.parse_args(args[1:]))
    cmd_handler = CommandHandler(
        command=command_name, args=[], kwargs=kw_args, retry_limit=0
    )
    print(cmd_handler.command.execute())


def execute_robot_flow(conf: str) -> None:
    """ This should trigger the standard execution flow """
    print("Standard execution flow")
    print(f"Conf file: {conf}")
    cmd_engine = CommandEngine()
    int_engine = InteractEngine(
        {"interacts": {}},
        cmd_engine.command_queue,
        cmd_engine.command_result_queue
    )
    eng_thread = Thread(target=cmd_engine.run, daemon=True)
    int_thread = Thread(target=int_engine.run, daemon=True)
    eng_thread.start()
    int_thread.start()
    while True:
        sleep(100000)


def main(args: list) -> None:
    """
    Main entrypoint for kitchen_aid package
    """
    if len(args) < 2:
        usage(args)
        return
    register_commands()
    if args[1] == "--config":
        execute_robot_flow(argv[2])
        return
    if args[1] == "--command":
        execute_command_flow(args[2:])
        return


if __name__ == "__main__":
    main(argv)
