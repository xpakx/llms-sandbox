from typing import Any, Literal, Type, Tuple
from typing import get_origin, get_args, Union
from types import UnionType
import argparse
from pathlib import Path
from enum import Enum
from collections.abc import Sequence, Iterable

from data import PathPart, CommandDefinition
from typedefs import CmdElem, CmdArg


class CommandSpecs:
    def __init__(self):
        self.specs = {}

    def is_flag_type(self, tp: Type[Any]) -> Tuple[bool, Type[Any] | None]:
        if tp in {int, float, str, bool, bytes, Path}:
            return True, tp

        if isinstance(tp, type) and issubclass(tp, Enum):
            return True, tp

        origin = get_origin(tp)
        args = get_args(tp)

        if origin is Literal:
            return True, tp

        if origin in {list, set, tuple, Sequence, Iterable}:
            if args:
                return self.is_flag_type(args[0])
            return True, tp

        is_union = origin is Union or (UnionType and origin is UnionType)
        if is_union:
            non_none_args = [arg for arg in args if arg is not type(None)]
            if len(non_none_args) == 1:
                return self.is_flag_type(non_none_args[0]), tp
            return False, None

        return False, None

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

    def transform_cmd_elems(self, path: list[CmdElem]) -> list[PathPart]:
        fragment_list: list[PathPart] = []
        for fragment in path:
            arg = False
            value = fragment
            if type(fragment) is CmdArg:
                arg = True
                value = fragment.name
            fragment_list.append(
                    PathPart(
                        name=value,
                        type="ARG" if arg else "CMD"
                    )
            )
        return fragment_list

    def add_to_specs(
            self,
            cmd_def: CommandDefinition,
            path: str | list[CmdElem] | None
    ):
        if type(path) is str:
            parsed_path = self.parse_path(path)
        elif not path:
            parsed_path = [PathPart("CMD", cmd_def.name)]
        else:
            parsed_path = self.transform_cmd_elems(path)

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
            is_flag, tp = self.is_flag_type(tp)
            if is_flag:
                print("flag candidate:", arg, tp.__name__)
                self.add_flag(curr, arg, tp, cmd_def)
        curr['defaults'] = {'cmd_key': cmd_def.name}
        curr['help'] = cmd_def.docs

    def ensure_subparsers(self, curr, curr_command):
        if 'subparsers' not in curr:
            curr['subparsers'] = {
                    'dest': f"{curr_command}_command" if curr_command else 'command',
                    'help': '',
                    'commands': {},
            }

    def add_flag(self, curr: dict, arg: str,
                 tp: Type[Any], cmd_def: CommandDefinition):
        var = {}
        help = cmd_def.arg_help.get(arg)
        if help:
            var['help'] = help
        flags = []
        flags.append(f"--{arg}")
        more_flags = cmd_def.flags.get(arg, [])
        if type(more_flags) is str:
            more_flags = [more_flags]
        flags.extend(more_flags)
        var['flags'] = flags
        if tp == bool:
            var['action'] = "store_true"
        else:
            var['type'] = tp
        self.ensure_args(curr)
        curr['args'].append(var)

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
