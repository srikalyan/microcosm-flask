"""
Test swagger naming conventions.

"""
from hamcrest import (
    assert_that,
    equal_to,
    is_,
)

from microcosm_flask.operations import Operation
from microcosm_flask.swagger.naming import operation_name, type_name


def test_operation_name_retrieve():
    name = operation_name(Operation.Retrieve, "foo")
    assert_that(name, is_(equal_to("retrieve")))


def test_operation_name_search_for():
    name = operation_name(Operation.SearchFor, ("foo", "bar"))
    assert_that(name, is_(equal_to("search_for_bars")))


def test_type_name_is_camel_case():
    name = type_name("foo_bar")
    assert_that(name, is_(equal_to("FooBar")))


def test_type_name_for_schema():
    name = type_name("foo_bar_schema")
    assert_that(name, is_(equal_to("FooBar")))
