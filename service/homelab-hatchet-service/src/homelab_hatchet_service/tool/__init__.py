import ast


def find_ast[T: ast.stmt](module: ast.Module, type: type[T], name: str) -> T:
    result = None
    for stmt in module.body:
        if (
            isinstance(stmt, type)
            and hasattr(stmt, "name")
            and getattr(stmt, "name") == name  # noqa: B009
        ):
            result = stmt
            break
    if not result:
        raise ValueError("Type {} name {} not found".format(type, name))
    return result
