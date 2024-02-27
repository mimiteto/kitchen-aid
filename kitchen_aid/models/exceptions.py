#! /usr/bin/env python3

""" Module provides various kitchen-aid specific exceptions. """


class GenericKitchenAidError(Exception):
    """ This is a catch-all kitchen-aid error """


class GenericCommandError(GenericKitchenAidError):
    """ This is a catch-all command error """


class RetriableError(GenericCommandError):
    """
    This error identifies a retriable error
    """


class CommandNotFound(GenericCommandError):
    """ This error identifies a command not found error """


class CommandTryAgain(RetriableError):
    """ This error identifies a command that should be retried """
