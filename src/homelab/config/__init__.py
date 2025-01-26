import deepmerge
import pulumi

from homelab.config.server import Server as Server


def __build(key: str) -> dict:
    return deepmerge.always_merger.merge(
        pulumi.Config().get_object(key, {}),
        pulumi.Config().get_object("stack-{}".format(key), {}),
    )


server = Server(**__build("server"))
