from six import add_metaclass
from six.moves import filter

from elasticsearch_dsl import DocType
from elasticsearch_dsl.field import Field

_MODEL_INDEX_MAPPING = {}


class Indexable(type):
    '''Defines an introspection type for Indexable Models.'''
    def __new__(cls, name, bases, namespace):
        fields = []
        # We introspect and collect the names of all the Fields in Index
        # to facilitate differentiating field attribute from non-field attribute
        # later.
        for k, x in namespace.items():
            if isinstance(x, Field):
                fields.append(k)
        # Append field-name information from all the Base classes.
        for base_index in filter(lambda x: issubclass(x, IndexedModel), bases):
            fields.extend(base_index._fields)
        # Insert fields into this class's namespace.
        namespace['_fields'] = fields

        # TODO: Assert sanity of extension class
        # -- Implement checking get_queryset and get_model implementations.
        klass = super(Indexable, cls).__new__(cls, name, bases, namespace)
        # Register this doctype in indexed models mapping.
        if 'model' in namespace:
            _MODEL_INDEX_MAPPING[namespace['model']] = klass
        return klass


@add_metaclass(Indexable)
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
                prep_method = getattr(self, 'prepare_{0}'.format(field))
                setattr(self, field, prep_method(obj))
            except AttributeError:
                val_from_obj_attr = getattr(obj, field)
                setattr(self, field, val_from_obj_attr)

    @classmethod
    def init_using_pk(cls, pk):
        obj = cls(_id=pk)
        return obj
