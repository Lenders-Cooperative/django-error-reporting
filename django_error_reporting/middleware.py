from uuid import uuid4
from django.conf import settings
from django.db import connection
from .utils import *


__all__ = [
    "ErrorReportingMiddleware"
]


class ErrorReportingMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response
        try:
            from ddtrace import tracer
            self.dd_scope = tracer.current_span()
        except:
            self.dd_scope = None

    def __call__(self, request):
        # Generate request_id from AWS load balancer trace ID or a UUID
        request_id = request.META.get(
            "HTTP_X_AMZN_TRACE_ID",
            str(uuid4())
        )

        request.session['trace_id'] = request_id

        #
        # Add event tags

        add_event_tag(
            "trace_id",
            request_id,
            self.dd_scope
        )

        if hasattr(settings, 'CODEBUILD_BUILD_NUMBER') and settings.CODEBUILD_BUILD_NUMBER:
            add_event_tag(
                "build_number",
                settings.CODEBUILD_BUILD_NUMBER,
                self.dd_scope
            )

        if hasattr(settings, 'CODEBUILD_RESOLVED_SOURCE_VERSION') and settings.CODEBUILD_RESOLVED_SOURCE_VERSION:
            add_event_tag(
                "build_commit",
                settings.CODEBUILD_RESOLVED_SOURCE_VERSION,
                self.dd_scope
            )

        if hasattr(connection, "schema_name"):
            add_event_tag(
                "schema",
                connection.schema_name,
                self.dd_scope
            )

        if request.user.is_authenticated:
            if hasattr(connection, "schema_name"):
                add_event_tag(
                    "schema_user_id",
                    f"{connection.schema_name}:{request.user.id}",
                    self.dd_scope
                )

                add_event_tag(
                    "schema_user_name",
                    f"{connection.schema_name}:{request.user.username or request.user.id}",
                    self.dd_scope
                )
            else:
                add_event_tag(
                    "user_id",
                    request.user.pk,
                    self.dd_scope
                )

            add_event_tag(
                "email",
                request.user.email or request.user.id,
                self.dd_scope
            )

        if hasattr(settings, "ERROR_REPORTING_TAGGING_CALLBACK"):
            settings.ERROR_REPORTING_TAGGING_CALLBACK(
                request,
                add_event_tag,
                self.dd_scope
            )

        return self.get_response(request)
