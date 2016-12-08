=====
Usage
=====

To use Django Elasticsearch Flex in a project, add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'elasticsearch_flex.apps.ElasticsearchFlexConfig',
        ...
    )

Add Django Elasticsearch Flex's URL patterns:

.. code-block:: python

    from elasticsearch_flex import urls as elasticsearch_flex_urls


    urlpatterns = [
        ...
        url(r'^', include(elasticsearch_flex_urls)),
        ...
    ]
