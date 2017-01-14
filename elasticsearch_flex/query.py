'''Django Compatible Search Queryset

This search queryset is a subset of django queryset wrapping over the low level
elasticsearch queries.
'''
from . import connections


class BaseSearchQuerySet(object):
    def __init__(self, index, **kwargs):
        self.index = index
        self._params = kwargs
        self._meta = {}

    @property
    def connection(self):
        return connections.get_connection()

    def _init_objects(self):
        hits = self._results['hits']['hits']
        if len(hits) == 0:
            return

        # TODO -- maybe keep the raw scores?
        ids = [hit['_id'] for hit in hits]
        qs = self.index().get_queryset()

        self._objects = qs.in_bulk(ids)
        keytype = type(self._objects.keys()[0])
        self._pks = list(map(keytype, ids))

    def _perform_search(self):
        raise NotImplementedError('Must use a subclass.')

    def _clone_with(self, params):
        qs = self.__class__(self.index, **self._params)
        qs._meta = self._meta.copy()
        qs._params.update(params)
        return qs

    def __iter__(self):
        for i in self._pks:
            yield self._objects[i]

    def __getitem__(self, key):
        pk = self._pks[key]
        return self._objects[pk]

    def __repr__(self):
        classname = self.__class__.__name__

        return '<{0} index={1}>'.format(classname, self.index)

    def search(self, **kwargs):
        qs = self._clone_with(kwargs)
        qs._perform_search()
        qs._init_objects()
        return qs


class TemplatedSearchQuerySet(BaseSearchQuerySet):
    def _perform_search(self):
        payload = {
            'id': self._meta['template_id'],
            'params': self._params,
        }
        ix_name = self.index._doc_type.index
        doc_type = self.index._doc_type.name

        self._results = self.connection.search_template(
            index=ix_name, doc_type=doc_type, body=payload)
        return self._results


class DSLProxySearchQuerySet(BaseSearchQuerySet):
    def _perform_search(self):
        pass

    def filter(self, *args, **kwargs):
        pass

    def sort(self, *args, **kwargs):
        pass

    def count(self, *args, **kwargs):
        pass


class DocQuerySet(BaseSearchQuerySet):
    def dsl(self):
        dpqs = DSLProxySearchQuerySet(self.index, **self._params)

    def use_template(self, name):
        tqs = TemplatedSearchQuerySet(self.index, **self._params)
        tqs._meta['template_id'] = '.'.join([self.index._meta.index, name])
        return tqs
