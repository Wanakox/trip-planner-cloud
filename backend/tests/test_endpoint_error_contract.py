"""Static safeguards for every domain-exception handler exposed by the API."""

import ast
from pathlib import Path

import pytest

ENDPOINTS = Path(__file__).parents[1] / "app" / "api" / "v1" / "endpoints"


def _exception_name(handler: ast.ExceptHandler) -> str | None:
    if isinstance(handler.type, ast.Name):
        return handler.type.id
    return None


def _http_exception_raise(handler: ast.ExceptHandler) -> ast.Raise | None:
    for node in ast.walk(handler):
        if (
            isinstance(node, ast.Raise)
            and isinstance(node.exc, ast.Call)
            and isinstance(node.exc.func, ast.Name)
            and node.exc.func.id == "HTTPException"
        ):
            return node
    return None


HANDLERS = [
    (source, handler)
    for source in ENDPOINTS.glob("*.py")
    for handler in ast.walk(ast.parse(source.read_text(encoding="utf-8")))
    if isinstance(handler, ast.ExceptHandler) and (_exception_name(handler) or "").endswith("Error")
]


@pytest.mark.parametrize(
    ("source", "handler"),
    HANDLERS,
    ids=lambda value: value.name if isinstance(value, Path) else _exception_name(value),
)
def test_domain_exceptions_are_translated_to_http(source: Path, handler: ast.ExceptHandler) -> None:
    raised = _http_exception_raise(handler)
    assert raised is not None, (
        f"{source.name}:{handler.lineno} handles {_exception_name(handler)} "
        "without raising HTTPException"
    )
    keywords = {keyword.arg: keyword.value for keyword in raised.exc.keywords}
    assert "status_code" in keywords
    assert "detail" in keywords
    detail = keywords["detail"]
    if isinstance(detail, ast.Constant):
        assert isinstance(detail.value, str) and detail.value.strip()


def test_every_endpoint_module_is_included_in_error_contract() -> None:
    modules_with_handlers = {source.stem for source, _ in HANDLERS}
    modules_without_domain_errors = {"__init__"}
    expected = {path.stem for path in ENDPOINTS.glob("*.py")} - modules_without_domain_errors
    assert modules_with_handlers == expected
