from pydantic import BaseModel, Field, IPvAnyAddress

from .record import RecordConfig


class NetworkConfig(BaseModel):
    public_ips: dict[str, IPvAnyAddress] = Field(alias="public-ips")
    public: RecordConfig
    private: RecordConfig
