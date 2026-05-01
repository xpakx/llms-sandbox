from typing import Callable, Any
from inspect import signature, getdoc

from data import CommandDefinition, ServiceData
from specification import CommandSpecs


class CommandDispatcher:
    def __init__(self):
        self.commands: dict[str, CommandDefinition] = {}
        self.services: dict[str, ServiceData] = {}
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
        parser = dispatcher.specs.parser()
        args = parser.parse_args()
        cmd_key = getattr(args, 'cmd_key', None)
        if cmd_key:
            dispatcher.dispatch(args.cmd_key, args)


dispatcher = CommandDispatcher()


@dispatcher.command('show {name} subscribe',
                    help={'name': 'name of the show',
                          'unsubscribe': 'unsubscribe the show'},
                    flags={'unsubscribe': ['-u']})
def subscribe(program: Any, name: str, unsubscribe: bool):
    '''
    Subscribing to show
    '''
    print("SUB", name)
    if unsubscribe:
        print("unsub")


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
