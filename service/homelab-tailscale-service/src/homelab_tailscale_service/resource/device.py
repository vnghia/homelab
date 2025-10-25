from __future__ import annotations

import os
import typing
from typing import Any

import httpx
from homelab_pydantic import HomelabBaseModel
from netaddr_pydantic import IPv4Address, IPv6Address
from pulumi import Output, ResourceOptions
from pulumi.dynamic import (
    CreateResult,
    DiffResult,
    Resource,
    ResourceProvider,
    UpdateResult,
)
from pydantic import ConfigDict, TypeAdapter, ValidationError

if typing.TYPE_CHECKING:
    from .. import TailscaleService


class TailscaleDevice(HomelabBaseModel):
    model_config = ConfigDict(extra="ignore")

    hostname: str
    addresses: list[str]


class TailscaleDevices(HomelabBaseModel):
    devices: list[TailscaleDevice]


class TailscaleDeviceProviderProps(HomelabBaseModel):
    model_config = ConfigDict(extra="ignore")

    hostname: str


class TailscaleDeviceProviderOutput(HomelabBaseModel):
    hostname: str
    v4: IPv4Address
    v6: IPv6Address


class TailscaleClient:
    @classmethod
    def devices(cls) -> TailscaleDevices:
        api_key = os.environ["TAILSCALE_API_KEY"]

        return TailscaleDevices.model_validate_json(
            httpx.get(
                "https://api.tailscale.com/api/v2/tailnet/-/devices",
                headers={"Authorization": "Bearer {}".format(api_key)},
            )
            .raise_for_status()
            .read()
        )

    @classmethod
    def device(cls, hostname: str) -> TailscaleDeviceProviderOutput:
        for device in cls.devices().devices:
            if device.hostname == hostname:
                return TailscaleDeviceProviderOutput(
                    hostname=device.hostname,
                    v4=TypeAdapter(IPv4Address).validate_python(device.addresses[0]),
                    v6=TypeAdapter(IPv6Address).validate_python(device.addresses[1]),
                )
        raise KeyError(
            "Could not found tailscale device with hostname {}".format(hostname)
        )


class TailscaleDeviceResourceProvider(ResourceProvider):
    RESOURCE_ID = "tailscale"

    serialize_as_secret_always = False

    def create(self, props: dict[str, Any]) -> CreateResult:
        tailscale_props = TailscaleDeviceProviderProps(**props)
        return CreateResult(
            id_=self.RESOURCE_ID,
            outs=TailscaleClient.device(tailscale_props.hostname).model_dump(
                mode="json"
            ),
        )

    def diff(self, _id: str, olds: dict[str, Any], news: dict[str, Any]) -> DiffResult:
        tailscale_olds = TailscaleDeviceProviderProps(**olds)
        try:
            tailscale_news = TailscaleDeviceProviderProps(**news)
            return DiffResult(changes=tailscale_olds != tailscale_news)
        except ValidationError:
            return DiffResult(changes=True)

    def update(
        self, _id: str, olds: dict[str, Any], news: dict[str, Any]
    ) -> UpdateResult:
        tailscale_props = TailscaleDeviceProviderProps(**news)
        return UpdateResult(
            outs=TailscaleClient.device(tailscale_props.hostname).model_dump(
                mode="json"
            ),
        )


class TailscaleDeviceResource(Resource, module="tailscale", name="Device"):
    v4: Output[IPv4Address]
    v6: Output[IPv6Address]

    def __init__(
        self, opts: ResourceOptions, tailscale_service: TailscaleService
    ) -> None:
        tailscale_container = tailscale_service.container
        super().__init__(
            TailscaleDeviceResourceProvider(),
            TailscaleDeviceResourceProvider.RESOURCE_ID,
            {"hostname": tailscale_container.resource.hostname, "v4": None, "v6": None},
            ResourceOptions.merge(
                opts, ResourceOptions(depends_on=tailscale_container.resource)
            ),
        )
