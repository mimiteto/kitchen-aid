#! /usr/bin/env python3

"""
Entrypoint for kitchen_aid package.
Use like:
    python3 -m kitchen_aid --config config
    OR
    python3 -m kitchen_aid --command command [with optional args]
"""

from sys import argv
import argparse

from kitchen_aid.models.command import CommandMapper, CommandHandler
from kitchen_aid.pkgs.commands.get_web_page import GetWebPage, HTTPRequest


def usage() -> None:
    """ Print usage """
    print("Usage: python3 -m kitchen_aid --config config")
    print("OR")
    print("Usage: python3 -m kitchen_aid --command command [with optional args]")
    print("Command args are specific to the command")


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


def execute_bot_flow(conf: str) -> None:
    """ This should trigger the standard execution flow """
    print("Standard execution flow")
    print(f"Conf file: {conf}")


def main(args: list) -> None:
    """
    Main entrypoint for kitchen_aid package
    """
    if len(args) < 2:
        usage()
        return
    register_commands()
    if args[1] == "--config":
        execute_bot_flow(argv[2])
        return
    if args[1] == "--command":
        execute_command_flow(args[2:])
        return


if __name__ == "__main__":
    main(argv)