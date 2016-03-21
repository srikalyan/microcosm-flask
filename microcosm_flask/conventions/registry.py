"""
Support for registering function metadata.

"""
from microcosm_flask.operations import Operation


REQUEST = "__request__"
RESPONSE = "__response__"
QS = "__qs__"


def iter_operations(graph, match_func):
    """
    Iterate through operations in matches.

    """
    for rule in graph.flask.url_map.iter_rules():
        try:
            operation, obj = Operation.parse(rule.endpoint)
        except (IndexError, ValueError):
            # operation follows a different convention (e.g. "static")
            continue
        else:
            # match_func gets access to rule to support path version filtering
            if match_func(operation, obj, rule):
                func = graph.flask.view_functions[rule.endpoint]
                yield operation, obj, rule, func


def request(schema):
    """
    Decorate a function with a request schema.

    """
    def wrapper(func):
        setattr(func, REQUEST, schema)
        return func
    return wrapper


def response(schema):
    """
    Decorate a function with a response schema.

    """
    def wrapper(func):
        setattr(func, RESPONSE, schema)
        return func
    return wrapper


def qs(schema):
    """
    Decorate a function with a query string schema.

    """
    def wrapper(func):
        setattr(func, QS, schema)
        return func
    return wrapper


def get_request_schema(func):
    return getattr(func, REQUEST, None)


def get_response_schema(func):
    return getattr(func, RESPONSE, None)


def get_qs_schema(func):
    return getattr(func, QS, None)