import ast


def find[T: ast.stmt](module: ast.Module, type: type[T], name: str) -> T:
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
        raise ValueError(f"Type {type} name {name} not found")
    return result


def add_keyword(
    function_def: ast.AsyncFunctionDef | ast.FunctionDef, keyword: ast.keyword
) -> None:
    for expr in function_def.decorator_list:
        if isinstance(expr, ast.Call):
            expr.keywords = [*expr.keywords, keyword]
            break
