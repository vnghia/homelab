import deepmerge
import pulumi

from homelab.config.docker import Docker
from homelab.config.network import Network


def __build(key: str) -> dict:
    return deepmerge.always_merger.merge(
        pulumi.Config().get_object(key, {}),
        pulumi.Config().get_object("stack-{}".format(key), {}),
    )


docker = Docker(**__build("docker"))
network = Network(**__build("network"))
