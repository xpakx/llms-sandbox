from dataclasses import dataclass
from typing import Callable, Any, Type
from typedefs import CmdFlag, CmdElem, CmdArg
from typing import TypeIs


class CmdCmd:
    def __init__(
            self,
            name: str,
    ):
        self.name = name
        self.type = 'CMD'


PathPart = CmdCmd | CmdArg


@dataclass
class CommandDefinition:
    name: str
    arguments: list[str]
    argument_types: dict[str, Type[Any]]
    func: Callable
    docs: str | None
    flags: dict[str, CmdFlag]
    arg_help: dict[str, str]
    path: str | list[CmdElem] | None = None,


@dataclass
class ServiceData:
    name: str
    type: Type[Any]
    service: Any


def is_cmd(val: PathPart) -> TypeIs[CmdCmd]:
    return val.type == 'CMD'


def is_arg(val: PathPart) -> TypeIs[CmdArg]:
    return val.type == 'ARG'
