from collections.abc import Mapping
from dataclasses import fields, is_dataclass
from typing import Any

from human_requests.abstraction import Output as _Output
from pydantic import BaseModel

from .catalog_sort import CatalogSort
from .regexes import RegexCountryAlias as _RegexCountryAlias
from .regexes import RegexLanguageTag as _RegexLanguageTag
from .regexes import RegexStoreId as _RegexStoreId

Output = _Output
RegexCountryAlias = _RegexCountryAlias
RegexLanguageTag = _RegexLanguageTag
RegexStoreId = _RegexStoreId

__all__ = [
    "Output",
    "RegexCountryAlias",
    "RegexLanguageTag",
    "RegexStoreId",
    "CatalogSort",
]

SCALAR_TYPES = (str, int, float, bool, bytes, type(None))
CONTAINER_TYPES = (Mapping, list, tuple, set)


def normalize(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return value.model_dump()
    return value


def is_leaf(value: Any) -> bool:
    value = normalize(value)
    return isinstance(value, SCALAR_TYPES + CONTAINER_TYPES)


def public_children_with_names(obj: Any) -> list[tuple[str, Any]]:
    result: list[tuple[str, Any]] = []

    if isinstance(obj, type):
        for name, value in vars(obj).items():
            if name.startswith("_"):
                continue
            if isinstance(value, (staticmethod, classmethod)):
                continue
            if callable(value) and not isinstance(value, type):
                continue
            result.append((name, value))
        return result

    if isinstance(obj, BaseModel):
        return []

    if is_dataclass(obj) and not isinstance(obj, type):
        for field in fields(obj):
            if field.name.startswith("_"):
                continue
            result.append((field.name, getattr(obj, field.name)))

    if hasattr(obj, "__dict__"):
        for name, value in vars(obj).items():
            if name.startswith("_"):
                continue
            if callable(value):
                continue
            result.append((name, value))

    for name, descriptor in vars(type(obj)).items():
        if name.startswith("_"):
            continue
        if isinstance(descriptor, property):
            result.append((name, getattr(obj, name)))

    return result


def registry_display_name(value: Any) -> str:
    if isinstance(value, type):
        return value.__qualname__.replace("<locals>.", "")
    return type(value).__qualname__.replace("<locals>.", "")


def collect_allowed_value_paths(parent: Any) -> list[str]:
    result: list[str] = []
    seen: set[int] = set()

    def walk(value: Any, path: list[str]) -> None:
        value = normalize(value)
        if is_leaf(value):
            result.append(".".join(path))
            return
        value_id = id(value)
        if value_id in seen:
            return
        seen.add(value_id)
        children = public_children_with_names(value)
        if not children:
            result.append(".".join(path))
            return
        for child_name, child_value in children:
            walk(child_value, [*path, child_name])

    walk(parent, [registry_display_name(parent)])
    return result


def collect_allowed_values(parent: Any) -> list[Any]:
    result: list[Any] = []
    seen: set[int] = set()

    def walk(value: Any) -> None:
        value = normalize(value)
        if is_leaf(value):
            result.append(value)
            return
        value_id = id(value)
        if value_id in seen:
            return
        seen.add(value_id)
        for _, child_value in public_children_with_names(value):
            walk(child_value)

    walk(parent)
    return result


def is_allowed_value(value: Any, parent: Any) -> bool:
    value = normalize(value)
    return value in collect_allowed_values(parent)


def find_registry_path(parent: Any, target: Any) -> str | None:
    seen: set[int] = set()

    def walk(value: Any, path: list[str]) -> str | None:
        if value is target:
            return ".".join(path)
        value = normalize(value)
        if is_leaf(value):
            return None
        value_id = id(value)
        if value_id in seen:
            return None
        seen.add(value_id)
        for child_name, child_value in public_children_with_names(value):
            found = walk(child_value, [*path, child_name])
            if found is not None:
                return found
        return None

    return walk(parent, [registry_display_name(parent)])


def validate_allowed_value(value: Any, parent: Any) -> Any:
    value = normalize(value)
    allowed = collect_allowed_values(parent)
    if value in allowed:
        return value
    if not is_leaf(value):
        value_path = find_registry_path(parent, value) or registry_display_name(value)
        allowed_paths = collect_allowed_value_paths(parent)
        raise ValueError(f"{value_path} is a value registry, not a value.\nUse one of:\n" + "\n".join(f"- {path}" for path in allowed_paths))
    raise ValueError(f"Invalid value {value!r}. Allowed values: {allowed!r}")
