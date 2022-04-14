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

## Settings

The following are settings available and their defaults:

### `ENABLE_DATADOG_INTEGRATION`

Indicates whether DataDog integrations should be processed.

Default: `True`

### `ENABLE_SENTRY_INTEGRATION`

Indicates whether Sentry integrations should be processed.

Default: `True`

### `DER_INCLUDE_REQUEST_TAGS`

Indicates whether event tags related to the request should be added.

These will include:
 * `http.client.ip_address` - remote client's IP address
 * `http.client.user_agent` - browner's user agent

## On Ready

When the app is loaded (i.e., `ready()` is called), it will do the following:
 * Load default settings into the project settings
 * Add `ErrorReportingMiddleware` to `settings.MIDDLEWARE`.
 * If DataDog integration is enabled, add `DataDogExceptionMiddleware` to `settings.MIDDLEWARE`. 


## Middleware

### `ErrorReportingMiddleware`

This middleware adds event tags (using `add_event_tag`) for each request. 

It also adds a `trace_id` to the session which is a unique identifier for a request. If using AWS load balancers, it will use the trace ID from it; otherwise, `uuid.uuid4()` is used.

To add app-specific tags, you can set a callback with `ERROR_REPORTING_TAGGING_CALLBACK` which should accept a `Request` instance and the `add_event_tag` function as arguments.

### `DataDogExceptionMiddleware`

When an exception is captured, this middleware will set the appropriate span tags on the root span of the trace. 

This middleware should be added as late as possible.

## Utilities

### `add_event_tag(name, value, dd_scope=None)`

Adds an event tag to the data sent to Sentry and/or DataDog. 
