__all__ = [
    "error_view"
]


def error_view(request):
    raise Exception("this is an exception")
