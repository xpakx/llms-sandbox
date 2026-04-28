from dataclasses import dataclass
from typing import Callable, Any
from inspect import signature


@dataclass
class CommandDefiniton:
    name: str
    arguments: list[str]
    func: Callable


class CommandDispatcher:
    def __init__(self):
        self.commands: dict[str, CommandDefiniton] = {}
        self.services: dict[str, Any] = {}
        self.preprocessors: dict[str, Callable] = {}

    def register(self, name: str, command: Callable):
        sig = signature(command)
        args = list(sig.parameters.keys())
        cmd_def = CommandDefiniton(
                name=name,
                func=command,
                arguments=args
        )
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
            if elem in self.services:
                kwargs[elem] = self.services.get(elem)
            else:
                value = vs.get(elem)
                if elem in self.preprocessors:
                    value = self.preprocessors[elem](value)
                kwargs[elem] = value
        cmd.func(**kwargs)

    def command(self, path: str | None = None, *, name: str = None):
        def decorator(f: Callable):
            registration_name = name if name else f.__name__
            self.register(registration_name, f)
            return f
        if callable(path):
            func = path
            return decorator(func)
        return decorator


dispatcher = CommandDispatcher()


@dispatcher.command
def subscribe(program: Any, name: str, unsubscribe: bool):
    print(name)


@dispatcher.command(name='find')
def test(program: Any, name: str):
    print(name)


if __name__ == "__main__":
    print(dispatcher.commands)
