from django.conf import settings
import sentry_sdk
import ddtrace


__all__ = [
    "add_event_tag",
]


def add_event_tag(name, value):
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
        ddtrace.tracer.current_span().set_tag(
            name,
            value
        )
    except:
        pass
