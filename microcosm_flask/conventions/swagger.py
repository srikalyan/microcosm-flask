"""
Swagger (OpenAPI) convention.

Exposes swagger definitions for matching operations.

"""
from flask import g

from microcosm.api import defaults
from microcosm_flask.conventions.base import Convention
from microcosm_flask.conventions.encoding import make_response
from microcosm_flask.conventions.registry import iter_endpoints
from microcosm_flask.namespaces import Namespace
from microcosm_flask.operations import Operation
from microcosm_flask.routing import make_path
from microcosm_flask.swagger.definitions import build_swagger


class SwaggerConvention(Convention):

    @property
    def matching_operations(self):
        return {
            Operation.from_name(operation_name)
            for operation_name in self.graph.config.swagger_convention.operations
        }

    def find_matching_endpoints(self, swagger_ns):
        """
        Compute current matching endpoints.

        Evaluated as a property to defer evaluation.

        """
        def match_func(operation, ns, rule):
            # only expose endpoints that have the correct path prefix and operation
            return (
                rule.rule.startswith(make_path(self.graph, swagger_ns.path)) and
                operation in self.matching_operations
            )

        return list(iter_endpoints(self.graph, match_func))

    def configure_discover(self, ns, definition):
        """
        Register a swagger endpoint for a set of operations.

        """
        @self.graph.route(ns.singleton_path, Operation.Discover, ns)
        def discover():
            swagger = build_swagger(self.graph, ns, self.find_matching_endpoints(ns))
            g.hide_body = True
            return make_response(swagger)


@defaults(
    name="swagger",
    operations=[
        "create",
        "create_for",
        "delete",
        "replace",
        "replace_for",
        "retrieve",
        "retrieve_for",
        "search",
        "search_for",
        "update",
        "update_batch",
    ],
    path_prefix="",
)
def configure_swagger(graph):
    """
    Build a singleton endpoint that provides swagger definitions for all operations.

    """
    ns = Namespace(
        path=graph.config.swagger_convention.path_prefix,
        subject=graph.config.swagger_convention.name,
        version=graph.config.swagger_convention.version,
    )
    convention = SwaggerConvention(graph)
    convention.configure(ns, discover=tuple())
    return ns.subject
