from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from . import tasks
from .indexes import get_index_for_model


@receiver(post_save)
def on_update_or_create(sender, instance, created, **kwargs):
    try:
        ix = get_index_for_model(sender)
    except KeyError:
        pass
    else:
        tasks.update_indexed_document.delay(ix, created, instance.pk)


@receiver(post_delete)
def on_model_delete(sender, instance, **kwargs):
    try:
        ix = get_index_for_model(sender)
    except KeyError:
        pass
    else:
        tasks.delete_indexed_document.delay(ix, instance.pk)


__all__ = ('on_update_or_create', 'on_model_delete')
