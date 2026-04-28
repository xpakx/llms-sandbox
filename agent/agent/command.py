from dataclasses import dataclass
from typing import Callable, Any, Literal
from inspect import signature


@dataclass
class PathPart:
    type: Literal["CMD", "ARG"]
    name: str


@dataclass
class CommandDefiniton:
    name: str
    arguments: list[str]
    func: Callable
    path: list[PathPart]


class CommandDispatcher:
    def __init__(self):
        self.commands: dict[str, CommandDefiniton] = {}
        self.services: dict[str, Any] = {}
        self.preprocessors: dict[str, Callable] = {}

    def register(self, name: str, command: Callable, path: str | None = None):
        sig = signature(command)
        args = list(sig.parameters.keys())
        cmd_def = CommandDefiniton(
                name=name,
                func=command,
                arguments=args,
                path=self.parse_path(path) if path else [PathPart("CMD", name)]
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
            # TODO: dispatch services by type
            if elem in self.services:
                kwargs[elem] = self.services.get(elem)
            else:
                value = vs.get(elem)
                if elem in self.preprocessors:
                    value = self.preprocessors[elem](value)
                kwargs[elem] = value
        cmd.func(**kwargs)

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

    def command(self, path: str | None = None, *, name: str = None):
        func = None
        if callable(path):
            func = path
            path = None

        def decorator(f: Callable):
            registration_name = name if name else f.__name__
            self.register(registration_name, f, path)
            return f
        if func:
            return decorator(func)
        return decorator


dispatcher = CommandDispatcher()


@dispatcher.command
def subscribe(program: Any, name: str, unsubscribe: bool):
    print(name)


@dispatcher.command("find {name}", name='find')
def test(program: Any, name: str):
    print(name)


if __name__ == "__main__":
    for cmd in dispatcher.commands.values():
        print(cmd.name)
        print(cmd.arguments)
        print(cmd.path)
        print("---")
