from django.conf import settings
from django_error_reporting.utils import *


def setup():
    print_debug("Setting up DataDog")

    # Add ddtrace app
    add_installed_app("ddtrace.contrib.django")

    # Add DataDog middleware
    add_middleware("django_error_reporting.middleware.DataDogExceptionMiddleware")

    setup_logging()

    print_debug("Finished setting up DataDog")


def setup_logging():
    if not settings.DER_SETUP_DATADOG_LOGGING:
        return

    # Add logger app
    add_installed_app("django_datadog_logger")

    # Add logger middleware
    add_middleware("django_datadog_logger.middleware.error_log.ErrorLoggingMiddleware")
    add_middleware("django_datadog_logger.middleware.request_log.RequestLoggingMiddleware")

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
