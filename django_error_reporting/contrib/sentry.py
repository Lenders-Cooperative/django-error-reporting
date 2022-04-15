from django.conf import settings
from django_error_reporting.utils import *
import sentry_sdk


def setup():
    print_debug("Setting up Sentry")

    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        debug=settings.DEBUG,
        traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
        integrations=settings.SENTRY_INTEGRATIONS,
        environment=settings.BASE_URL,
        release=settings.CODEBUILD_BUILD_NUMBER,
        send_default_pii=True,
        before_send=None,
        request_bodies="never"
    )

    print_debug("Finished setting up Sentry")
