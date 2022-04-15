import logging
from django.conf import settings
import sentry_sdk
import ddtrace


__all__ = [
    "add_event_tag", "capture_exception", "capture_message", "add_middleware", "add_installed_app", "print_debug",
]


logger = logging.getLogger("root")


def add_event_tag(name, value, dd_scope=None):
    """
    Attempts to add an event tag for Sentry and DataDog
    """
    try:
        sentry_sdk.set_tag(
            name,
            value
        )
    except:
        pass

    try:
        if dd_scope:
            dd_scope.set_tag(
                name,
                value
            )
        else:
            ddtrace.tracer.current_span().set_tag(
                name,
                value
            )
    except:
        pass


def sentry_before_send(event, _hint):
    print(f"{event}")

    if hasattr(settings, "SENTRY_BEFORE_SEND_CB"):
        settings.SENTRY_BEFORE_SEND_CB(event, _hint)


def send_full_request_body():
    if hasattr(settings, "DER_SEND_FULL_REQUEST_BODY_CB"):
        send_request = settings.DER_SEND_FULL_REQUEST_BODY_CB()

    return "always"


def sentry_init():
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        debug=settings.DEBUG,
        traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
        integrations=settings.SENTRY_INTEGRATIONS,
        environment=settings.BASE_URL,
        release=settings.CODEBUILD_BUILD_NUMBER,
        send_default_pii=True,
        before_send=sentry_before_send,
        request_bodies=None
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


def add_middleware(middleware, add_early=False):
    if middleware not in settings.MIDDLEWARE:
        if add_early:
            settings.MIDDLEWARE = [middleware] + settings.MIDDLEWARE
        else:
            settings.MIDDLEWARE.append(middleware)


def add_installed_app(app):
    if app not in settings.INSTALLED_APPS:
        settings.INSTALLED_APPS.append(app)


def print_debug(msg):
    if settings.DEBUG:
        print(f"[DER] {msg}")
