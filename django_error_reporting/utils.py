import logging
from django.conf import settings
import sentry_sdk
import ddtrace
from sentry_sdk import VERSION as sentry_sdk_version
from .constants import SENTRY_V2

__all__ = [
    "add_event_tag", "capture_exception", "capture_message", "print_debug", "is_sentry_v2"
]


logger = logging.getLogger(__name__)


def add_event_tag(name, value, dd_scope=None):
    """
    Attempts to add an event tag for Sentry and DataDog
    """
    if "datadog" in settings.DER_ENABLED_INTEGRATIONS:
        if not dd_scope:
            dd_scope = ddtrace.tracer.current_root_span()

        if not dd_scope:
            dd_scope = ddtrace.tracer.current_span()

        try:
            dd_scope.set_tag(
                name,
                value
            )
        except Exception as e:
            logger.warning(f"Unable to set DataDog span tag '{name}': {e}")

    if "sentry" in settings.DER_ENABLED_INTEGRATIONS:
        try:
            sentry_sdk.set_tag(
                name,
                value
            )
        except Exception as e:
            logger.warning(f"Unable to set Sentry tag '{name}': {e}")


def sentry_before_send(event, _hint):
    print(f"{event}")

    if hasattr(settings, "SENTRY_BEFORE_SEND_CB"):
        settings.SENTRY_BEFORE_SEND_CB(event, _hint)


def send_full_request_body():
    if hasattr(settings, "DER_SEND_FULL_REQUEST_BODY_CB"):
        send_request = settings.DER_SEND_FULL_REQUEST_BODY_CB()

    return "always"


def sentry_init():
    version_kwargs = (
        {
            "max_request_body_size": None
        } if is_sentry_v2() else {
            "request_bodies": None
        }
    )

    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        debug=settings.DEBUG,
        traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
        integrations=settings.SENTRY_INTEGRATIONS,
        environment=settings.BASE_URL,
        release=settings.CODEBUILD_BUILD_NUMBER,
        send_default_pii=True,
        before_send=sentry_before_send,
        **version_kwargs,
    )


def capture_exception(e):
    """
    Wrapper for sentry_sdk.capture_exception.  Use this instead of that one
    """
    logger.exception("Received error: [%s]", e)
    sentry_sdk.capture_exception(e)


def capture_message(e):
    """
    Wrapper for sentry_sdk.capture_message.  Use this instead of that one
    """
    logger.info("Received message: [%s]", e)
    sentry_sdk.capture_message(e)


def print_debug(msg):
    if settings.DEBUG:
        print(f"[DER] {msg}")


def is_sentry_v2():
    """
    Check if Sentry SDK version is 2.0.0 or higher
    """
    return sentry_sdk_version >= SENTRY_V2