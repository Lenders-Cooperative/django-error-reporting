# Django Error Reporting
Global error reporting framework for Django, Sentry, and DataDog

## Requirements

* **Python** >= 3.6
* **django** >= 2.2.9
* **sentrysdk** >= 1.5.4 
* **ddtrace** >=0.59.0
* **django-datadog-logger** >= 0.5.0

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

### General

#### `DER_ENABLED_INTEGRATIONS`

Tuple of enabled integrations.

Default: `("datadog", "sentry")`


#### `DER_INCLUDE_REQUEST_TAGS`

Indicates whether event tags related to the request should be added.

These will include:
 * `http.client.ip_address` - remote client's IP address
 * `http.client.user_agent` - browner's user agent

### General Logging

#### `DER_LOGGING_LEVEL`

Minimum logging level for logs output by DER.

Defaults to `ERROR`.

### DataDog Logging

#### `DER_SETUP_DATADOG_LOGGING`

Indicates whether to setup DataDog logging using `django-datadog-logger`.

#### `DER_DATADOG_LOGGING_LEVEL`

Minimum logging level for logs output for DataDog.

Defaults to `DER_LOGGING_LEVEL`.

#### `DER_DATADOG_LOGGING_TO_CONSOLE`

Indicates whether to send all DataDog logs to console.

Defaults to `False`

#### `DER_DATADOG_LOGGING_FILE`

Log file for DataDog.

Defaults to `None` which disables file logging.

### Sentry Logging

#### `DER_SENTRY_LOGGING_LEVEL`

Minimum logging level for logs output for Sentry.

Defaults to `DER_LOGGING_LEVEL`.

## On Ready

When the app is loaded (i.e., `ready()` is called), it will do the following:
 * Load default settings into the project settings
 * Add `ErrorReportingMiddleware` to `MIDDLEWARE`.
 * If DataDog integration is enabled:
   * Add `DataDogExceptionMiddleware` to `MIDDLEWARE`
   * Add `ddtrace.contrib.django` to `INSTALLED_APPS`
   * If DataDog logging is enabled:
     * Add `django_datadog_logger` to `INSTALLED_APPS`
     * Add `ErrorLoggingMiddleware` and `RequestLoggingMiddleware` to `MIDDLEWARE`
     * Set `LOGGING` with formatters, handlers, and loggers.


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

### `add_middleware(middleware, add_early=False)`

Add a middleware to `settings.MIDDLEWARE` after checking for its existence.

If `add_early`, middleware is prepended to the list. Otherwise, it is appended.

### `add_installed_app(app)`

Add an app to `settings.INSTALLED_APPS` after checking for its existence. 

### `print_debug(msg)`

If `settings.DEBUG` is `True`, print `msg`.
