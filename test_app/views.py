import logging


__all__ = [
    "error_view", "logging_view"
]


def error_view(request):
    raise Exception("this is an exception")


def logging_view(request):
    logger = logging.getLogger(__name__)
    logger.error("This is a test log message")
