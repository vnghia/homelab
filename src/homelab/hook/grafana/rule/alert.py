from typing import Any

import pulumiverse_grafana as grafana
from homelab_docker.extract import ExtractorArgs
from homelab_docker.extract.global_ import GlobalExtractor
from homelab_pydantic import DictAdapter
from pulumi import Output, ResourceOptions

from . import schema


def to_expression(model: schema.AlertRuleExpression) -> str:
    return model.model_dump_json(
        by_alias=False, exclude_defaults=True, exclude_none=True
    ).replace("from_", "from")


def to_args(
    spec: str,
) -> grafana.alerting.v0alpha1.AlertRuleSpecArgs:
    model = schema.AlertRuleSpec.model_validate_json(spec)
    return grafana.alerting.v0alpha1.AlertRuleSpecArgs(
        annotations={k: v.root for k, v in model.annotations.items()}
        if model.annotations
        else None,
        exec_err_state=model.exec_err_state,
        expressions={k: to_expression(v) for k, v in model.expressions.root.items()},
        for_=model.for_,
        keep_firing_for=model.keep_firing_for,
        labels={k: v.root for k, v in model.labels.items()} if model.labels else None,
        missing_series_evals_to_resolve=model.missing_series_evals_to_resolve,
        no_data_state=model.no_data_state,
        notification_settings=grafana.alerting.v0alpha1.AlertRuleSpecNotificationSettingsArgs(
            contact_point=model.notification_settings.receiver,
            active_timings=[
                i.root for i in model.notification_settings.active_time_intervals
            ]
            if model.notification_settings.active_time_intervals
            else None,
            group_bies=model.notification_settings.group_by,
            group_interval=model.notification_settings.group_interval.root
            if model.notification_settings.group_interval
            else None,
            group_wait=model.notification_settings.group_wait.root
            if model.notification_settings.group_wait
            else None,
            mute_timings=[
                i.root for i in model.notification_settings.mute_time_intervals
            ]
            if model.notification_settings.mute_time_intervals
            else None,
            repeat_interval=model.notification_settings.repeat_interval.root
            if model.notification_settings.repeat_interval
            else None,
        )
        if model.notification_settings
        else None,
        panel_ref={
            "dashboard_uid": model.panel_ref.dashboard_uid,
            "panel_id": str(model.panel_ref.panel_id),
        }
        if model.panel_ref
        else None,
        paused=model.paused,
        title=model.title,
        trigger=grafana.alerting.v0alpha1.AlertRuleSpecTriggerArgs(
            interval=model.trigger.interval.root
        ),
    )


def provision_alert_rule(
    uid: str,
    folder_uid: Output[str] | None,
    config: dict[str, Any],
    opts: ResourceOptions,
    extractor_args: ExtractorArgs,
) -> None:
    grafana.alerting.v0alpha1.AlertRule(
        uid,
        opts=opts,
        metadata=grafana.alerting.v0alpha1.AlertRuleMetadataArgs(
            uid=uid, folder_uid=folder_uid
        ),
        spec=(
            Output.json_dumps(
                GlobalExtractor.extract_recursively(config["spec"], extractor_args)
            ).apply(to_args)
        ),
    )
