from dataclasses import dataclass
from typing import Callable, Any, Literal, Type
from typedefs import CmdFlag


@dataclass
class PathPart:
    type: Literal["CMD", "ARG"]
    name: str


@dataclass
class CommandDefinition:
    name: str
    arguments: list[str]
    argument_types: dict[str, Type[Any]]
    func: Callable
    docs: str | None
    flags: dict[str, CmdFlag]
    arg_help: dict[str, str]


@dataclass
class ServiceData:
    name: str
    type: Type[Any]
    service: Any
