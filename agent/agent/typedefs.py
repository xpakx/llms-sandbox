class CmdArg:
    def __init__(
            self,
            name: str,
            *,
            help: str | None = None,
    ):
        self.name = name
        self.help = help


CmdElem = str | CmdArg


class CmdFlag:
    def __init__(
            self,
            name: str,
            *,
            aliases: list[str] | str | None = None,
            help: str | None = None,
    ):
        self.name = name
        if type(aliases) is str:
            self.aliases = [aliases]
        else:
            self.aliases = aliases
        self.help = help
