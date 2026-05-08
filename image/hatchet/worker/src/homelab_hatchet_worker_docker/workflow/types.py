import dataclasses
import logging
from typing import Any, Self

from hatchet_sdk import Hatchet, Worker
from hatchet_sdk.clients.rest.models.workflow import Workflow as WorkflowData
from hatchet_sdk.runnables.workflow import BaseWorkflow
from homelab_hatchet_tool.worker import NAMESPACE_SEPARATOR
from homelab_pydantic import add_namespace

logger = logging.getLogger("workflow")


@dataclasses.dataclass
class Workflow:
    data: WorkflowData
    model: BaseWorkflow[Any]

    @classmethod
    def add_namespace(cls, namespace: str | None, name: str) -> str:
        return add_namespace(namespace, name, separator=NAMESPACE_SEPARATOR)

    @classmethod
    def from_model(cls, hatchet: Hatchet, model: BaseWorkflow[Any]) -> Self:
        rows = hatchet.workflows.list(model.name).rows
        data = None
        if rows:
            for row in rows:
                if row.name == model.name:
                    data = row
        if not data:
            raise RuntimeError(
                "Expecting workflow named {}, got {}".format(model.name, rows)
            )
        return cls(data=data, model=model)

    @classmethod
    def register_model(
        cls,
        hatchet: Hatchet,
        worker: Worker,
        namespace: str | None,
        model: Any,
    ) -> Self | None:
        if not isinstance(model, BaseWorkflow):
            raise ValueError("Object {} is not a valid workflow".format(model))
        if model._config.name.startswith(NAMESPACE_SEPARATOR):
            model._config.name = model._config.name.removeprefix(NAMESPACE_SEPARATOR)
        else:
            model._config.name = cls.add_namespace(namespace, model._config.name)
        logger.info("Registering workflow {}".format(model.name))

        try:
            worker.register_workflow(model)
        except Exception as exception:
            logger.exception(exception)
            return None
        return cls.from_model(hatchet, model)

    @classmethod
    def register_models(
        cls, hatchet: Hatchet, worker: Worker, namespace: str | None, models: list[Any]
    ) -> dict[str, Self]:
        return {
            workflow.name: workflow
            for model in models
            if (workflow := cls.register_model(hatchet, worker, namespace, model))
        }

    @property
    def id(self) -> str:
        return self.data.metadata.id

    @property
    def name(self) -> str:
        return self.data.name
