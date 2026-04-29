import typing

from homelab_pydantic import HomelabBaseModel
from pulumi import Output

if typing.TYPE_CHECKING:
    from . import PlainArgs


class GlobalPlainExtractContextSource(HomelabBaseModel):
    pcontext: str

    def extract_str(self, plain_args: PlainArgs) -> Output[str]:
        return plain_args.contexts[self.pcontext]
