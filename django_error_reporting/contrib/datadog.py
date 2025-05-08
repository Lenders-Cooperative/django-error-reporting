from django.conf import settings
from django.utils.log import configure_logging
from django_error_reporting.utils import *
import ddtrace


def setup():
    print_debug("Setting up DataDog")

    if "django_error_reporting.middleware.DataDogExceptionMiddleware" not in settings.MIDDLEWARE:
        raise NotImplementedError("Missing django_error_reporting.middleware.DataDogExceptionMiddleware in MIDDLEWARE")

    if settings.DER_SETUP_DATADOG_LOGGING:
        print_debug("Setting up DataDog logging")
        setup_logging()

    if "CELERY_BROKER_URL" in dir(settings):
        print_debug("Detected Celery broker URL and patched in ddtrace")
        ddtrace.patch(celery=True)

    print_debug("Finished setting up DataDog")


def setup_logging():
    if "django_datadog_logger" not in settings.INSTALLED_APPS:
        raise NotImplementedError("Missing django_datadog_logger in INSTALLED_APPS")

    for middleware in ["error_log.ErrorLoggingMiddleware", "request_log.RequestLoggingMiddleware"]:
        middleware_name = f"django_datadog_logger.middleware.{middleware}"
        if middleware_name not in settings.MIDDLEWARE:
            raise NotImplementedError(f"Missing {middleware_name} in MIDDLEWARE")

    ddtrace.patch(logging=True)

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

    logger_handlers = ["datadog-console"]

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

    # Reconfigure Django logging
    # https://github.com/django/django/blob/7119f40c9881666b6f9b5cf7df09ee1d21cc8344/django/__init__.py#L19
    configure_logging(
        settings.LOGGING_CONFIG,
        settings.LOGGING
    )

    try:
        from celery.signals import after_setup_logger, after_setup_task_logger

        @after_setup_logger.connect
        def on_after_setup_logger(logger, *args, **kwargs):
            from django_datadog_logger.formatters.datadog import DataDogJSONFormatter

            for handler in list(logger.handlers):
                handler.setFormatter(DataDogJSONFormatter())

        @after_setup_task_logger.connect
        def on_after_setup_task_logger(logger, *args, **kwargs):
            from django_datadog_logger.formatters.datadog import DataDogJSONFormatter

            for handler in list(logger.handlers):
                handler.setFormatter(DataDogJSONFormatter())

    except ImportError:
        pass
