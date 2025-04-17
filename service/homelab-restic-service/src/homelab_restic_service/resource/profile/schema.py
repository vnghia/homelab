import json
from pathlib import Path

from homelab_docker.resource.file.config import JsonDefaultModel


# TODO: use Pydantic BaseModel after https://github.com/koxudaxi/datamodel-code-generator/issues/1851
class ResticProfileModel(JsonDefaultModel):
    jsonschema = json.loads(Path(__file__).with_name("schema.json").read_text())
