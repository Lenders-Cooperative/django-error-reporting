from django.conf import settings
from django_error_reporting.utils import *


def setup():
    print_debug("Setting up DataDog")

    if "ddtrace.contrib.django" not in settings.INSTALLED_APPS:
        raise NotImplementedError("Missing ddtrace.contrib.django in INSTALLED_APPS")

    if "django_error_reporting.middleware.DataDogExceptionMiddleware" not in settings.MIDDLEWARE:
        raise NotImplementedError("Missing django_error_reporting.middleware.DataDogExceptionMiddleware in MIDDLEWARE")

    setup_logging()

    print_debug("Finished setting up DataDog")


def setup_logging():
    if not settings.DER_SETUP_DATADOG_LOGGING:
        return

    if "django_datadog_logger" not in settings.INSTALLED_APPS:
        raise NotImplementedError("Missing django_datadog_logger in INSTALLED_APPS")

    for middleware in ["error_log.ErrorLoggingMiddleware", "request_log.RequestLoggingMiddleware"]:
        middleware_name = f"django_datadog_logger.middleware.{middleware}"
        if middleware_name not in settings.MIDDLEWARE:
            raise NotImplementedError(f"Missing {middleware_name} in MIDDLEWARE")

    if "datadog" not in settings.LOGGING["formatters"]:
        settings.LOGGING["formatters"]["datadog"] = {
            "()": "django_datadog_logger.formatters.datadog.DataDogJSONFormatter"
        }

    # Handlers

    logging_level = settings.DER_DATADOG_LOGGING_LEVEL or settings.DER_LOGGING_LEVEL

    if "datadog-console" not in settings.LOGGING["handlers"]:
        settings.LOGGING["handlers"]["datadog-console"] = {
            "level": logging_level,
            "class": "logging.StreamHandler",
            "formatter": "datadog"
        }

    if "datadog-file" not in settings.LOGGING["handlers"] and settings.DER_DATADOG_LOGGING_FILE:
        settings.LOGGING["handlers"]["datadog-file"] = {
            "level": logging_level,
            "class": "logging.FileHandler",
            "filename": settings.DER_LOGGING_DATADOG_FILE,
            "formatter": "datadog"
        }

    # Loggers

    logger_handlers = []

    if settings.DER_DATADOG_LOGGING_TO_CONSOLE:
        logger_handlers.append("datadog-console")

    if "datadog-file" in settings.LOGGING["handlers"]:
        logger_handlers.append("datadog-file")

    settings.LOGGING["loggers"].update({
        "django_datadog_logger.middleware.error_log": {
            "handlers": logger_handlers,
            "level": "INFO",
            "propagate": False
        },
        "django_datadog_logger.middleware.request_log": {
            "handlers": logger_handlers,
            "level": "INFO",
            "propagate": False
        },
        "django_datadog_logger.rest_framework": {
            "handlers": logger_handlers,
            "level": "INFO",
            "propagate": False
        },
    })
