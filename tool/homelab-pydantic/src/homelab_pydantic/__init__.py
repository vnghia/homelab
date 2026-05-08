from pydantic import BaseModel as BaseModel

from . import docker as docker
from .hostname import Hostname as Hostname
from .hostname import Hostnames as Hostnames
from .model import DictAdapter as DictAdapter
from .model import HomelabBaseModel as HomelabBaseModel
from .model import HomelabRootModel as HomelabRootModel
from .model import HomelabServiceConfigDict as HomelabServiceConfigDict
from .model import Json as Json
from .model import JsonAdapter as JsonAdapter
from .network import IPvAnyAddressAdapter as IPvAnyAddressAdapter
from .network import IPvAnyNetworkAdapter as IPvAnyNetworkAdapter
from .path import AbsolutePath as AbsolutePath
from .path import RelativePath as RelativePath


def add_namespace(
    namespace: str | None, name: str | None, *, separator: str = "-"
) -> str:
    if namespace:
        return namespace + ((separator + name) if name else "")
    if name:
        return ((namespace + separator) if namespace else "") + name
    raise ValueError("Either namespace of name must not be null")
