import deepmerge
import pulumi

from homelab.config.docker import Docker


def __build(key: str) -> dict:
    return deepmerge.always_merger.merge(
        pulumi.Config().get_object(key, {}),
        pulumi.Config().get_object("stack-{}".format(key), {}),
    )


docker = Docker(**__build("docker"))
