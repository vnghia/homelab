from pydantic import BaseModel, ConfigDict, Field


class Dns(BaseModel):
    model_config = ConfigDict(strict=True)

    zone_id: str = Field(alias="zone-id")
    records: dict[str, str]


class DnsMap(BaseModel):
    public: Dns
    private: Dns
