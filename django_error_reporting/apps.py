from django.apps import AppConfig
from django.conf import settings as DjSettings
import django_error_reporting.settings as DERSettings
import sentry_sdk
import django_error_reporting.contrib
from .utils import *


class DjangoErrorReportingConfig(AppConfig):
    name = "django_error_reporting"
    verbose_name = "Django Error Reporting"

    def ready(self):
        print_debug("Loading...")

        #
        # Check for our middleware

        if "django_error_reporting.middleware.ErrorReportingMiddleware" not in DjSettings.MIDDLEWARE:
            raise NotImplementedError("Missing django_error_reporting.middleware.ErrorReportingMiddleware in MIDDLEWARE")

        #
        # Load our settings into Django

        for key in dir(DERSettings):
            if hasattr(DjSettings, key) or key.startswith("_") or key in ["logging"]:
                continue
            setattr(DjSettings, key, getattr(DERSettings, key))

        #
        # Logger settings

        for key in ["formatters", "handlers", "loggers"]:
            if key not in DjSettings.LOGGING:
                DjSettings.LOGGING[key] = {}

        if "version" not in DjSettings.LOGGING:
            DjSettings.LOGGING["version"] = 1

        #
        # Run integration setups

        for integration in DjSettings.DER_ENABLED_INTEGRATIONS:
            if not hasattr(django_error_reporting.contrib, integration):
                raise NotImplementedError(f"Integration {integration} is not available")

            module = getattr(django_error_reporting.contrib, integration)

            if not hasattr(module, "setup"):
                raise NotImplementedError(f"Integration {integration} is missing the setup function")

            getattr(module, "setup")()

        print_debug("Finished loading...")
