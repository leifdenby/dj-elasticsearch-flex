from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

__version__ = '0.1.0'


default_app_config = 'elasticsearch_flex.apps.ElasticsearchFlexConfig'

if hasattr(settings, 'ElasticsearchFlex'):
    'host' in settings.ElasticsearchFlex
