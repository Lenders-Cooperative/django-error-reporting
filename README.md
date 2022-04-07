# Django Error Reporting
Global error reporting framework for Django, Sentry, and DataDog

## Requirements

* **Python** >= 3.6
* **django** >= 2.2.9
* **sentrysdk** >= 1.5.4 
* **ddtrace** >=0.59.0  

## Installation

Install `django-error-reporting`:
```
pip install django-error-reporting
```

Add it to your `INSTALLED_APPS`:
```python
INSTALLED_APPS = (
    ...
    "django_error_reporting",
    ...
)
```

Add the middleware:
```python
MIDDLEWARE = [
    ...
    "django_error_reporting.middleware.ErrorReportingMiddleware",
    ...
]
```
_Note: to capture user data, middleware needs to be after `django.contrib.auth.middleware.AuthenticationMiddleware`._

## Middleware

### `ErrorReportingMiddleware`

This middleware adds event tags (using `add_event_tag`) for each request. 

It also adds a `trace_id` to the session which is a unique identifier for a request. If using AWS load balancers, it will use the trace ID from it; otherwise, `uuid.uuid4()` is used.

To add app-specific tags, you can set a callback with `ERROR_REPORTING_TAGGING_CALLBACK` which should accept a `Request` instance and the `add_event_tag` function as arguments.  

## Utilities

### `add_event_tag(name, value)`

To add an event tag to the data sent to Sentry or DataDog, you need to this function. 
