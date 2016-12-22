import logging

from django.conf import settings
from elasticsearch_dsl.connections import connections

__version__ = '0.1.0'

logger = logging.getLogger('elasticsearch_flex')

default_app_config = 'elasticsearch_flex.apps.ElasticsearchFlexConfig'

if hasattr(settings, 'ElasticsearchFlex'):
    'host' in settings.ElasticsearchFlex

__all__ = ('connections',)
