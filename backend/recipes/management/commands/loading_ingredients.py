from csv import reader

from django.core.management import BaseCommand

from recipes.models import Ingredient, Tag


class Command(BaseCommand):
    help = 'Load ingredients data from csv-file to DB.'

    def handle(self, *args, **kwargs):
        with open(
                'recipes/data/ingredients.csv', 'r',
                encoding='UTF-8') as ingredients:
            for row in reader(ingredients):
                name, measurement_unit = row
                Ingredient.objects.get_or_create(
                    name=name, measurement_unit=measurement_unit,
                )
        self.stdout.write(self.style.SUCCESS('Ингредиенты загружены.'))

        with open(
                'recipes/data/tags.csv', 'r',
                encoding='UTF-8') as tags:
            for row in reader(tags):
                (name, color, slug) = row
                Tag.objects.get_or_create(
                    name=name, color=color, slug=slug,
                )
        self.stdout.write(self.style.SUCCESS('Теги загружены.'))
