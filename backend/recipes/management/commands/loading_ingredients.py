import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from recipes.models import Ingredient


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            'filemane',
            default='ingredients.csv',
            nargs='?',
            type=str
        )

    def handle(self, *args, **options):
        try:
            with open(os.path.join(
                    settings.BASE_DIR,
                    'data',
                    options['filename']),
                    'r',
                    encoding='utf-8') as f:
                data = csv.render(f)
                for row in data:
                    name, measurement_unit = row
                    Ingredient.objects.get_or_create(
                        name=name, measurement_unit=measurement_unit)
        except FileNotFoundError:
            raise CommandError('Добавьте файл ingredients в папку data')
