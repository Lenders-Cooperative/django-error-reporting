from uuid import uuid4
import logging
from django.conf import settings
from django.db import connection
from .utils import *


__all__ = [
    "ErrorReportingMiddleware",
]

logger = logging.getLogger(__name__)


class ErrorReportingMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

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
            request_id
        )

        if hasattr(settings, 'CODEBUILD_BUILD_NUMBER') and settings.CODEBUILD_BUILD_NUMBER:
            add_event_tag(
                "build_number",
                settings.CODEBUILD_BUILD_NUMBER
            )

        if hasattr(settings, 'CODEBUILD_RESOLVED_SOURCE_VERSION') and settings.CODEBUILD_RESOLVED_SOURCE_VERSION:
            add_event_tag(
                "build_commit",
                settings.CODEBUILD_RESOLVED_SOURCE_VERSION
            )

        if hasattr(connection, "schema_name"):
            add_event_tag(
                "schema",
                connection.schema_name
            )

        if request.user.is_authenticated:
            if hasattr(connection, "schema_name"):
                add_event_tag(
                    "schema_user_id",
                    f"{connection.schema_name}:{request.user.id}"
                )

                add_event_tag(
                    "schema_user_name",
                    f"{connection.schema_name}:{request.user.username or request.user.id}"
                )
            else:
                add_event_tag(
                    "user_id",
                    request.user.pk
                )

            add_event_tag(
                "email",
                request.user.email or request.user.id
            )

        add_event_tag(
            "http.headers.user_ip_address",
            request.META.get(settings.DER_HEADERS_IP_ADDRESS)
        )

        if settings.DER_HEADER_TAGS:
            for tag_name, meta_key in settings.DER_HEADER_TAGS.iteritems():
                add_event_tag(
                    tag_name,
                    request.META.get(meta_key)
                )

        if hasattr(settings, "DER_REQUEST_TAGGING_CB") and settings.DER_REQUEST_TAGGING_CB:
            settings.DER_REQUEST_TAGGING_CB(
                request,
                add_event_tag
            )

        return self.get_response(request)
