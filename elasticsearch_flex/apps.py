# -*- coding: utf-8
from importlib import import_module

from django.conf import settings
from django.apps import AppConfig


class ElasticsearchFlexConfig(AppConfig):
    name = 'elasticsearch_flex'

    def ready(self):
        # Discover the modules
        import elasticsearch_flex.signals
        for app_name in settings.INSTALLED_APPS:
            module = '{}.search_indexes'.format(app_name)
            try:
                import_module(module)
            except ImportError:
                pass
