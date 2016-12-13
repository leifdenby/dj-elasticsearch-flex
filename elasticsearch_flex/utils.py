import functools


def rgetattr(obj, attr, allow_null=True):
    attrs = attr.split('__')

    def _get_attr(o, a):
        try:
            return getattr(o, a)
        except AttributeError as e:
            if not allow_null:
                raise e

    return functools.reduce(_get_attr, [obj] + attrs)
