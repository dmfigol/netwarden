import enum


class SSHParseMethod(enum.Enum):
    TEXTFSM = enum.auto()
    GENIE = enum.auto()

    NULL = enum.auto()
