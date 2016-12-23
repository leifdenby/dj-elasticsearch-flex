'''Django Compatible Search Queryset

This search queryset is a subset of django queryset wrapping over the low level
elasticsearch queries.
'''
from . import connections


class TemplateQuerySet(object):
    '''QuerySet like object for template queries'''

    def __init__(self, index, id, **params):
        self.index = index
        self.template_id = id
        self.params = params

    def __get_item__(self, key):
        pass

    def __iter__(self):
        pass

    def _perform_search(self):
        c = connections.get_connection()

        payload = {
            'id': self.template_id,
            'params': self.params,
        }
        ix_name = self.index._doc_type.index
        doc_type = self.index._doc_type.name

        res = c.search_template(index=ix_name, doc_type=doc_type, body=payload)

        # TODO -- load objects from model.
