from homelab_pydantic import HomelabBaseModel, RelativePath


class GlobalExtractIncludeSource(HomelabBaseModel):
    include: RelativePath
