"""
Generalized error handling.

"""
from logging import getLogger

from flask import jsonify
from werkzeug.exceptions import default_exceptions


error_logger = getLogger("errors")


def extract_status_code(error):
    """
    Extract an error code from a message.

    """
    try:
        return error.code
    except AttributeError:
        try:
            return error.status_code
        except AttributeError:
            try:
                return error.errno
            except AttributeError:
                return 500


def extract_error_message(error):
    """
    Extract a useful message from an error.

    Prefer the description attribute, then the message attribute, then
    the errors string conversion. In each case, fall back to the error class's
    name in the event that the attribute value was set to a uselessly empty string.

    """
    try:
        return error.description or error.__class__.__name__
    except AttributeError:
        try:
            return str(error.message) or error.__class__.__name__
        except AttributeError:
            return str(error) or error.__class__.__name__


def extract_context(error):
    """
    Extract extract context from an error.

    Errors may (optionally) provide a context attribute which will be encoded
    in the response.

    """
    return getattr(error, "context", {})


def extract_retryable(error):
    """
    Extract a retryable status from an error.

    It's not usually helpful to retry on an error, but it's useful to do so
    when the application knows it might.

    """
    return getattr(error, "retryable", False)


def make_json_error(error):
    """
    Handle errors by logging and
    """
    message = extract_error_message(error)
    status_code = extract_status_code(error)
    context = extract_context(error)
    retryable = extract_retryable(error)

    # Flask will not log user exception (fortunately), but will log an error
    # for exceptions that escape out of the application entirely (e.g. if the
    # error handler raises an error)
    error_logger.debug("Handling {} error: {}".format(
        status_code,
        message,
    ))

    # Serialize into JSON response
    response_data = {
        "context": context,
        "message": message,
        "retryable": retryable,
    }

    response = jsonify(**response_data)
    response.status_code = status_code
    return response


def configure_error_handlers(graph):
    """
    Register error handlers.

    """

    # override all of the werkzeug HTTPExceptions
    for code in default_exceptions.iterkeys():
        graph.flask.error_handler_spec[None][code] = make_json_error

    # register catch all for user exceptions
    graph.flask.error_handler_spec[None][None] = [(Exception, make_json_error)]
