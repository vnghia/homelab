from __future__ import annotations

import typing

from homelab_pydantic import HomelabBaseModel

if typing.TYPE_CHECKING:
    from . import PlainArgs


class GlobalPlainExtractHostnameSource(HomelabBaseModel):
    hostname: str
    record: str | None = None
    scheme: str | None = None
    append_slash: bool = False

    def to_hostname(self, plain_args: PlainArgs) -> str:
        record = self.record or plain_args.host
        if record is None:
            raise ValueError("Record or host must be supplied for hostname extract")
        return plain_args.hostnames[record][self.hostname].value

    def to_url(self, plain_args: PlainArgs) -> str:
        hostname = self.to_hostname(plain_args)
        if self.scheme:
            hostname = "{}://{}{}".format(
                self.scheme, hostname, "/" if self.append_slash else ""
            )
        return hostname

    def extract_str(self, plain_args: PlainArgs) -> str:
        return self.to_url(plain_args)
