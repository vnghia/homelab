from enum import StrEnum, auto


class TraefikDynamicType(StrEnum):
    HTTP = auto()
    TCP = auto()
