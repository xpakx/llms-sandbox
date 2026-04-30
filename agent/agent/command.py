from dataclasses import dataclass
from typing import Callable, Any, Literal, Type
from typing import get_origin, get_args, Union
from types import UnionType
from inspect import signature, getdoc
import argparse
from pathlib import Path
from enum import Enum
from collections.abc import Sequence, Iterable


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
    flags: dict[str, list[str] | str]
    arg_help: dict[str, str]


class CommandSpecs:
    def __init__(self):
        self.specs = {}

    def is_flag_type(self, tp: Type[Any]) -> bool:
        if tp in {int, float, str, bool, bytes, Path}:
            return True

        if isinstance(tp, type) and issubclass(tp, Enum):
            return True

        origin = get_origin(tp)
        args = get_args(tp)

        if origin is Literal:
            return True

        if origin in {list, set, tuple, Sequence, Iterable}:
            if args:
                return self.is_flag_type(args[0])
            return True

        is_union = origin is Union or (UnionType and origin is UnionType)
        if is_union:
            non_none_args = [arg for arg in args if arg is not type(None)]
            if len(non_none_args) == 1:
                return self.is_flag_type(non_none_args[0])
            return False

        return False

    def parse_path(self, path: str) -> list[PathPart]:
        fragment_list: list[PathPart] = []
        fragments = path.split()
        for fragment in fragments:
            arg = False
            if fragment[0] == '{' and fragment[-1] == '}':
                arg = True
                fragment = fragment[1:-1]
            if not fragment.isalpha():
                print(f"Part of path {fragment} is incorrect")
                continue
            fragment_list.append(
                    PathPart(
                        name=fragment,
                        type="ARG" if arg else "CMD"
                    )
            )
        return fragment_list

    def add_to_specs(self, cmd_def: CommandDefinition, path: str | None):
        parsed_path = self.parse_path(path) if path else [PathPart("CMD", cmd_def.name)]
        curr = self.specs
        curr_command = None
        used_args = set()
        for elem in parsed_path:
            if elem.type == "CMD":
                self.ensure_subparsers(curr, curr_command)
                curr = curr['subparsers']['commands'].setdefault(elem.name, {})
                curr_command = elem.name
            else:
                self.ensure_args(curr)
                match = next((d for d in curr['args'] if elem.name in d['flags']), None)
                if not match:
                    arg_type = cmd_def.argument_types.get(elem.name, str)
                    curr['args'].append({
                        'flags': [elem.name],
                        'type': arg_type,
                        'help': cmd_def.arg_help.get(elem.name, ''),
                    })
                else:
                    help = cmd_def.arg_help.get(elem.name)
                    if help and match['help']:
                        print(f"WARNING: redefining help for {elem.name}")
                    if help:
                        match['help'] = help
                    arg_type = cmd_def.argument_types.get(elem.name, str)
                    if arg_type != match['type']:
                        print(f"WARNING: `{elem.name}` was already defined as "
                              f"{match['type'].__name__} but `{cmd_def.name}()` "
                              f"tries to redefine it as {arg_type.__name__}."
                              )
                used_args.add(elem.name)

        for arg in cmd_def.arguments:
            tp = cmd_def.argument_types.get(arg)
            if not tp or arg in used_args:
                continue
            if self.is_flag_type(tp):
                print("flag candidate:", arg)
        curr['defaults'] = {'cmd_key': cmd_def.name}
        curr['help'] = cmd_def.docs

    def ensure_subparsers(self, curr, curr_command):
        if 'subparsers' not in curr:
            curr['subparsers'] = {
                    'dest': f"{curr_command}_command" if curr_command else 'command',
                    'help': '',
                    'commands': {},
            }

    def ensure_args(self, curr):
        if 'args' not in curr:
            curr['args'] = []

    def build_parser(self, spec: dict, parser=None) -> argparse.ArgumentParser:
        if parser is None:
            parser = argparse.ArgumentParser(
                    description=spec.get("description", ""))

        for arg in spec.get("args", []):
            flags = arg.pop("flags")
            parser.add_argument(*flags, **arg)

        if "defaults" in spec:
            parser.set_defaults(**spec["defaults"])

        if "subparsers" in spec:
            sp_spec = spec["subparsers"]
            subparsers = parser.add_subparsers(
                dest=sp_spec["dest"], help=sp_spec.get("help")
            )
            for name, cmd_spec in sp_spec.get("commands", {}).items():
                parser_args = {
                    k: v
                    for k, v in cmd_spec.items()
                    if k not in ["args", "subparsers", "defaults"]
                }
                sub = subparsers.add_parser(name, **parser_args)
                self.build_parser(cmd_spec, parser=sub)

        return parser

    def parser(self) -> argparse.ArgumentParser:
        return self.build_parser(self.specs)


class CommandDispatcher:
    def __init__(self):
        self.commands: dict[str, CommandDefinition] = {}
        self.services: dict[str, Any] = {}
        self.preprocessors: dict[str, Callable] = {}
        self.specs = CommandSpecs()

    def register(
            self,
            name: str,
            command: Callable,
            path: str | None = None,
            flags: dict[str, list[str] | str] | None = None,
            help: dict[str, str] | None = None,
    ):
        sig = signature(command)
        args = list(sig.parameters.keys())
        docs = getdoc(command)
        types = {
            k: v.annotation
            for k, v in sig.parameters.items()
            if v.annotation is not v.empty
        }
        cmd_def = CommandDefinition(
                name=name,
                func=command,
                arguments=args,
                argument_types=types,
                docs=docs,
                flags=flags if flags else {},
                arg_help=help if help else {},
        )
        self.specs.add_to_specs(cmd_def, path)
        self.commands[name] = cmd_def

    def add_service(self, name: str, service: Any):
        self.services[name] = service

    def add_preprocessor(self, name: str, processor: Callable):
        self.preprocessors[name] = processor

    def dispatch(self, name, args):
        cmd = self.commands.get(name)
        if not cmd:
            return
        kwargs = {}
        vs = vars(args)
        for elem in cmd.arguments:
            # TODO: dispatch services by type
            if elem in self.services:
                kwargs[elem] = self.services.get(elem)
            else:
                value = vs.get(elem)
                tp = cmd.argument_types.get(elem)
                if tp and tp is not str and tp is not Any:
                    value = tp(value)
                if elem in self.preprocessors:
                    value = self.preprocessors[elem](value)
                kwargs[elem] = value
        cmd.func(**kwargs)

    def command(
            self,
            path: str | None = None,
            *,
            name: str | None = None,
            flags: dict[str, list[str] | str] | None = None,
            help: dict[str, str] | None = None,
    ):
        func = None
        if callable(path):
            func = path
            path = None

        def decorator(f: Callable):
            registration_name = name if name else f.__name__
            self.register(registration_name, f,
                          path=path, flags=flags, help=help)
            return f
        if func:
            return decorator(func)
        return decorator

    def run(self):
        # TODO: pass services, detect and define flags
        parser = dispatcher.specs.parser()
        args = parser.parse_args()
        cmd_key = getattr(args, 'cmd_key', None)
        if cmd_key:
            dispatcher.dispatch(args.cmd_key, args)


dispatcher = CommandDispatcher()


@dispatcher.command('show {name} subscribe', help={'name': 'name of the show'})
def subscribe(program: Any, name: str, unsubscribe: bool):
    '''
    Subscribing to show
    '''
    print("SUB", name)


@dispatcher.command("show {name} find")
def test(program: Any, name: str):
    '''Finding show'''
    print("FIND", name)


@dispatcher.command("show {name}")
def show(program: Any, name: str):
    print("SHOW", name)


if __name__ == "__main__":
    print(dispatcher.specs.specs)
    dispatcher.run()
