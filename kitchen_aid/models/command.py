#! /usr/bin/env python3

"""
This module provides base command and result utilities
"""

from dataclasses import dataclass
from typing import Callable, Type


@dataclass
class Result:
    """
    Base result class.
    All commands are expected to return a result object or a derived class
    """

    success: bool
    message: str
    errors: list[Exception | str]

    def get_byte_message(self) -> bytes:
        """
        Returns the message as a byte string
        """
        return self.message.encode("utf-8")


class RetriableError(Exception):
    """
    This error identifies a retriable error
    """


class FailedOperation(Exception):
    """
    This error identifies a failed operation
    """

    def __init__(self, message: str, undo_result: Result | None = None) -> None:
        self.undo_result = undo_result
        super().__init__(message)


class Command:
    """
    Base command class.
    All commands are expected to inherit from this class
    """

    can_undo: bool = False

    def execute(self) -> Result:
        """
        All commands are expected to implement this method
        """
        raise NotImplementedError

    def undo(self) -> Result:
        """
        All commands are expected to implement this method
        """
        raise NotImplementedError

    def redo(self) -> Result:
        """
        All commands are expected to implement this method
        """
        raise NotImplementedError


# pylint: disable=too-few-public-methods
class CommandHandler:
    """
    Base command handler class.
    All command handlers are expected to inherit from this class
    """

    def __init__(
        self,
        command: Type[Command],
        args: list | None,
        kwargs: dict | None,
        retry_limit: int = 3,
    ) -> None:
        if args is None:
            args = []
        if kwargs is None:
            kwargs = {}
        self.command = command(*args, **kwargs)
        self.retry_limit = retry_limit

    def _execute(self, exec: Callable) -> Result:
        """
        Executable utility.
        It will raise OperationError if the operation fails more than the retry limit
        """
        retries = 0
        result: Result | None = None
        errors: list[str] = []
        while retries <= self.retry_limit:
            try:
                result = exec()
            except RetriableError as error:
                retries += 1
                errors.append(str(error))
            else:
                break
        if isinstance(result, Result):
            return result
        raise FailedOperation(
            f"Operation failed execution after {
                self.retry_limit} retries: {errors}"
        )

    def execute(self) -> Result:
        """
        All command handlers are expected to implement this method
        """
        result: Result | None = None
        errors: list[str] = []
        try:
            result = self._execute(self.command.execute)
        except FailedOperation as error:
            errors.append(str(error))
        if isinstance(result, Result):
            return result
        if self.command.can_undo:
            result = self.command.undo()
        raise FailedOperation(
            f"Operation failed after {self.retry_limit} retries: {errors}",
            undo_result=result,
        )
