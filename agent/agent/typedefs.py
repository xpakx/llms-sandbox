class CmdArg:
    def __init__(self, name: str):
        self.name = name


CmdElem = str | CmdArg
