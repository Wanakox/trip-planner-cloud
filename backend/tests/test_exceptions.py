"""Regression tests for every user-facing domain exception."""

import inspect

import pytest

from app.core import exceptions


def domain_exception_classes() -> list[type[exceptions.TripPlannerError]]:
    """Return all concrete exceptions so new ones are covered automatically."""
    return [
        exception_class
        for _, exception_class in inspect.getmembers(exceptions, inspect.isclass)
        if issubclass(exception_class, exceptions.TripPlannerError)
        and exception_class is not exceptions.TripPlannerError
        and exception_class.__module__ == exceptions.__name__
    ]


@pytest.mark.parametrize("exception_class", domain_exception_classes())
def test_domain_exception_has_a_user_facing_default_message(
    exception_class: type[exceptions.TripPlannerError],
) -> None:
    error = exception_class()

    assert str(error) == exception_class.default_message
    assert str(error).strip()
    assert str(error).endswith(".")


@pytest.mark.parametrize("exception_class", domain_exception_classes())
def test_domain_exception_accepts_a_more_specific_message(
    exception_class: type[exceptions.TripPlannerError],
) -> None:
    error = exception_class("Mensaje específico para esta operación.")

    assert str(error) == "Mensaje específico para esta operación."


def test_base_exception_also_has_a_safe_fallback_message() -> None:
    assert str(exceptions.TripPlannerError()) == "Se ha producido un error en TripPlanner."


def test_all_exported_error_classes_inherit_from_the_common_base() -> None:
    error_classes = [
        exception_class
        for name, exception_class in inspect.getmembers(exceptions, inspect.isclass)
        if name.endswith("Error") and exception_class.__module__ == exceptions.__name__
    ]

    assert error_classes
    assert all(
        issubclass(error_class, exceptions.TripPlannerError) for error_class in error_classes
    )
