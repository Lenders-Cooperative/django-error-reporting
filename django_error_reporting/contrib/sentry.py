from urllib.parse import urlparse
from sentry_sdk.integrations.django.transactions import LEGACY_RESOLVER
from django.conf import settings
from django_error_reporting.utils import *
import sentry_sdk


def setup():
    print_debug("Setting up Sentry")

    if not settings.DER_SENTRY_DSN:
        raise NotImplementedError("DER_SENTRY_DSN setting is missing")

    def urlconf_callback():
        return "config.urls"

    def before_send(event, _hint):
        print_debug(f"Sentry event: {event}")

        if "request" in event and "url" in event["request"]:
            path = urlparse(event["request"]["url"]).path
            urlconf = urlconf_callback()
            event["transaction"] = LEGACY_RESOLVER.resolve(path, urlconf=urlconf)

        return event
    
    version_kwargs = (
        {
            "max_request_body_size": settings.DER_SENTRY_REQUEST_BODIES
        } if is_sentry_v2() else {
            "request_bodies": settings.DER_SENTRY_REQUEST_BODIES
        }
    )

    sentry_sdk.init(
        dsn=settings.DER_SENTRY_DSN,
        debug=settings.DER_SENTRY_DEBUG or settings.DEBUG,
        traces_sample_rate=settings.DER_SENTRY_TRACES_SAMPLE_RATE,
        integrations=settings.DER_SENTRY_INTEGRATIONS,
        environment=settings.DER_SENTRY_ENV,
        release=settings.DER_SENTRY_RELEASE,
        send_default_pii=True,
        before_send=before_send,
        **version_kwargs,
    )

    print_debug("Finished setting up Sentry")
