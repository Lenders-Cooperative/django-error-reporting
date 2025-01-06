# Django Error Reporting
Global error reporting framework for Django, Sentry, and DataDog

## Requirements

* **Python** >= 3.6
* **django** >= 2.2.9
* **sentrysdk** >= 1.5.4 
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
    "django_error_reporting.apps.DjangoErrorReportingConfig",
    ...
)
```

Add this to your `MIDDLEWARE`:
```python
MIDDLEWARE = (
    ...
    "django_error_reporting.middleware.ErrorReportingMiddleware"
)
```




#### Log Ingestion

If you plan on implementing log ingestion, you'll also have to do the following:

Add this to your `INSTALLED_APPS`:
```python
INSTALLED_APPS = (
    ...
    "django_datadog_logger"
)
```

And this to your `MIDDLEWARE`:
```python
MIDDLEWARE = (
    ...
    "django_datadog_logger.middleware.error_log.ErrorLoggingMiddleware",
    "django_datadog_logger.middleware.request_log.RequestLoggingMiddleware",
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
 * `http.headers.ip_address` - remote IP address (see `DER_HEADERS_IP_ADDRESS`)

#### `DER_HEADERS_IP_ADDRESS`

If `DER_INCLUDE_REQUEST_TAGS` is enabled, this defines the IP address header. This needs to correspond to a HTTP header in the format accepted by [`request.META`](https://docs.djangoproject.com/en/4.0/ref/request-response/#django.http.HttpRequest.META).

Defaults to `REMOTE_ADDR`.

#### `DER_HEADER_TAGS`

A dictionary of headers to convert to event tags in the format of `{<tag name>: <META name>}` where `<META name>` is the key acccepted by [`request.META`](https://docs.djangoproject.com/en/4.0/ref/request-response/#django.http.HttpRequest.META).


Defaults to `None`. 

### Sentry

#### `DER_SENTRY_DSN`

Your Sentry DSN.

Default: `None`

#### `DER_SENTRY_INTEGRATIONS`

List of Sentry integrations.

Default: `[]`

#### `DER_SENTRY_TRACES_SAMPLE_RATE`

Float for sample rate.

Default: `0.0`

#### `DER_SENTRY_ENV`

Environment name for Sentry.

Default: `local`

#### `DER_SENTRY_REQUEST_BODIES`

Request bodies setting.

Default: `always`

#### `DER_SENTRY_RELEASE`

Release.

Default: `"0"`.

#### `DER_SENTRY_DEBUG`

Indicates if Sentry should use debug mode.

Defaults to `settings.DEBUG`.

### General Logging

#### `DER_LOGGING_LEVEL`

Minimum logging level for logs output by DER.

Defaults to `ERROR`.

### DataDog


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

Log file for DataDog. This must correspond to 

Defaults to `None` which disables file logging.

### Sentry Logging

#### `DER_SENTRY_LOGGING_LEVEL`

Minimum logging level for logs output for Sentry.

Defaults to `DER_LOGGING_LEVEL`.

## On Ready

When the app is loaded (i.e., `ready()` is called), it will do the following:
 * Load default settings into the project settings
 * If DataDog integration is enabled:
   * Verify installed apps and middleware were added and throw `NotImplementedError` for missing.
     * If DataDog logging is enabled:
       * Verify installed apps and middleware were added and throw `NotImplementedError` for missing.
       * Set `LOGGING` with formatters, handlers, and loggers.
 * If Sentry integration is enabled:
   * Verify `DER_SENTRY_DSN` is set and throw `NotImplementedError` if missing.
   * Initialize Sentry.


## Middleware

### `ErrorReportingMiddleware`

This middleware adds event tags (using `add_event_tag`) for each request. 

It also adds a `trace_id` to the session which is a unique identifier for a request. If using AWS load balancers, it will use the trace ID from it; otherwise, `uuid.uuid4()` is used.

To add app-specific tags, you can set a callback with `ERROR_REPORTING_TAGGING_CALLBACK` which should accept a `Request` instance and the `add_event_tag` function as arguments.

### `DataDogExceptionMiddleware`

When an exception is captured, this middleware will set the appropriate span tags on the root span of the trace. 

This middleware should be added as late as possible.

## Contrib

For each implementation, there is a module in `contrib` and it must contain a `setup()` function which will be called during `ready()` to initialize and perform start-up tasks. 

## Utilities

### `add_event_tag(name, value, dd_scope=None)`

Adds an event tag to the data sent to Sentry and/or DataDog. 

### `print_debug(msg)`

If `settings.DEBUG` is `True`, print `msg`.
