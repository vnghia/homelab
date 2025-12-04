from .base import ResticHostBase


class ResticS3Host(ResticHostBase):
    s3: str

    @property
    def prefix(self) -> str:
        return "s3"
