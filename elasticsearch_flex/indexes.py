from collections import namedtuple
from six import add_metaclass
from six.moves import filter

from elasticsearch_dsl.document import DocType, DocTypeMeta

from .fields import FlexField
from .utils import rgetattr

_MODEL_INDEX_MAPPING = {}

FieldAttrMap = namedtuple('FieldAttrMap', ('name', 'attr'))


class IndexableMeta(type):
    '''Defines an introspection type for Indexable Models.'''
    def __new__(cls, name, bases, namespace):
        fields = []
        # We introspect and collect the names of all the Fields in Index
        # to facilitate differentiating field attribute from non-field attribute
        # later.
        for k, x in namespace.items():
            if isinstance(x, FlexField):
                f = x._model_attr if x._model_attr is not None else k
                fields.append(FieldAttrMap(k, f))
        # Append field-name information from all the Base classes.
        ix_predicate = lambda x: issubclass(x, DocType) and hasattr(x, '_fields')
        for base_index in filter(ix_predicate, bases):
            fields.extend(base_index._fields)
        # Insert fields into this class's namespace.
        namespace['_fields'] = fields

        # TODO: Assert sanity of extension class
        # -- Implement checking get_queryset and get_model implementations.
        klass = super(IndexableMeta, cls).__new__(cls, name, bases, namespace)
        # Register this doctype in indexed models mapping.
        if 'model' in namespace:
            _MODEL_INDEX_MAPPING[namespace['model']] = klass
        return klass


class IndexableDocTypeMeta(IndexableMeta, DocTypeMeta):
    pass


@add_metaclass(IndexableDocTypeMeta)
class IndexedModel(DocType):
    '''Base class for declaring Index for a Model.

    This class is an extension of Elasticsearch-DSL's DocType. For the fields,
    as a convention, it is assumed that the model has the attribute of the
    same name. This default behaviour can be controlled by implementing a
    `prepare_<FieldName>` method, accepting the object instance.
    '''
    def get_queryset(self):
        return self.queryset

    def get_object(self):
        qs = self.get_queryset()
        return qs.get(pk=self._id)

    @property
    def object(self):
        return self.get_object()

    def prepare(self):
        obj = self.get_object()
        for field in self._fields:
            try:
                prep_method = getattr(self, 'prepare_{0}'.format(field.attr))
                setattr(self, field.name, prep_method(obj))
            except AttributeError:
                val_from_obj_attr = rgetattr(obj, field.attr)
                setattr(self, field.name, val_from_obj_attr)

    @classmethod
    def init_using_pk(cls, pk):
        obj = cls(_id=pk)
        return obj


def get_index_for_model(model):
    try:
        return _MODEL_INDEX_MAPPING[model]
    except KeyError:
        raise KeyError('Model {0} has no associated index'.format(model))


def get_model_for_index(index):
    try:
        rev_map = (m for m, i in _MODEL_INDEX_MAPPING.items() if i is index)
        return next(rev_map, None)
    except StopIteration:
        raise KeyError('Index {0} has no associated model'.format(index))


def registered_indices():
    return _MODEL_INDEX_MAPPING.values()

__all__ = (
    'IndexedModel',
    'get_index_for_model',
    'get_model_for_index',
    'registered_indices',
)
