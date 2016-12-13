# coding: utf-8
from tqdm import tqdm

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    args = '<nb>'
    help = 'Generate events with random data'

    def handle(self, nb=20, *args, **options):
        pass
