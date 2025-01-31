from typing import Any

import deepmerge
import pulumi

from homelab_config.common import constant as constant
from homelab_config.common import get_name as get_name
from homelab_config.docker import Docker
from homelab_config.integration import Integration
from homelab_config.network import Network


def __build(key: str) -> dict[Any, Any]:
    return deepmerge.always_merger.merge(
        pulumi.Config().get_object(key, {}),
        pulumi.Config().get_object("stack-{}".format(key), {}),
    )


docker = Docker(**__build("docker"))
network = Network(**__build("network"))
integration = Integration(**__build("integration"))
