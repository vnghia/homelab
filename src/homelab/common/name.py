from homelab.common import constant


def get_name(name: str | None, project: bool = False, stack: bool = True):
    return "-".join(
        ([constant.PROJECT_NAME] if project or not name else [])
        + ([name] if name else [])
        + ([constant.PROJECT_STACK] if stack else [])
    )
