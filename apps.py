from django.apps import AppConfig


class CurdserviceConfig(AppConfig):
    name = 'CURDService'

    def ready(self):
        super(CurdserviceConfig, self).ready()
        from django.utils.module_loading import autodiscover_modules
        autodiscover_modules('my_curd')
