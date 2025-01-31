import os

import pulumi

PROJECT_NAME = os.environ.get("PULUMI_PROJECT_NAME", pulumi.get_project())
PROJECT_STACK = pulumi.get_stack()
PROJECT_LABELS = {
    "pulumi.project": PROJECT_NAME,
    "pulumi.stack": PROJECT_STACK,
}
