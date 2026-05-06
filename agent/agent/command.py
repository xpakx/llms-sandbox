from typing import Callable, Any
from inspect import signature, getdoc

from data import CommandDefinition, ServiceData
from specification import CommandSpecs
from typedefs import CmdElem, CmdFlag


class CommandDispatcher:
    def __init__(self):
        self.commands: dict[str, CommandDefinition] = {}
        self.services: dict[str, ServiceData] = {}
        self.preprocessors: dict[str, Callable] = {}
        self.specs = CommandSpecs()
        self.flag_data: dict[str, list[CmdFlag]] = {}

    def register(
            self,
            name: str,
            command: Callable,
            path: str | list[CmdElem] | None = None,
            flags: list[CmdFlag] | None = None,
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
        flag_dict = {}
        if flags:
            for flag in flags:
                flag_dict[flag.name] = flag
        cmd_def = CommandDefinition(
                name=name,
                func=command,
                arguments=args,
                argument_types=types,
                docs=docs,
                flags=flag_dict,
                arg_help=help if help else {},
        )
        # TODO: defer adding to spec until we know we
        # have all data, as some might be defined
        # separately, e.g. in @app.flag decorator
        self.specs.add_to_specs(cmd_def, path)
        self.commands[name] = cmd_def

    def add_service(self, name: str, service: Any):
        self.services[name] = ServiceData(
                name=name,
                service=service,
                type=service.__class__
        )

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
                service = self.services.get(elem)
                kwargs[elem] = service.service if service else None
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
            path: str | list[CmdElem] | None = None,
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
        parser = self.specs.parser()
        args = parser.parse_args()
        cmd_key = getattr(args, 'cmd_key', None)
        if cmd_key:
            self.dispatch(args.cmd_key, args)

    def save_flag_data(self, flag: CmdFlag, func: Callable):
        cmd_flags = self.flag_data.setdefault(func.__name__, [])
        cmd_flags.append(flag)
        for f in cmd_flags:
            print(f.name, f.aliases, f.help)

    def flag(
            self,
            name: str,
            *,
            aliases: list[str] | str | None = None,
            help: str | None = None,
    ):
        flag = CmdFlag(name, aliases=aliases, help=help)

        def decorator(f: Callable):

            self.save_flag_data(flag, f)
            return f
        return decorator
