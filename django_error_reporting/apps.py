from django.apps import AppConfig
from django.conf import settings as DjSettings
import django_error_reporting.settings as DERSettings


class DjangoErrorReportingConfig(AppConfig):
    name = "django_error_reporting"
    verbose_name = "Django Error Reporting"

    def ready(self):
        # Load our settings into Django
        for key in dir(DERSettings):
            if hasattr(DjSettings, key) or key.startswith("_") or key in ["logging"]:
                continue
            setattr(DjSettings, key, getattr(DERSettings, key))
