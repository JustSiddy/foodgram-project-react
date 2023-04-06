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
                name = row
                measurement_unit = row
                Ingredient.objects.get_or_create(
                    name=name[0], measurement_unit=measurement_unit[1],
                )
        self.stdout.write(self.style.SUCCESS('Ингредиенты загружены.'))

        with open(
                'recipes/data/tags.csv', 'r',
                encoding='UTF-8') as tags:
            for row in reader(tags):
                name = row
                color = row
                slug = row
                Tag.objects.get_or_create(
                    name=name[0], color=color[1], slug=slug[2],
                )
        self.stdout.write(self.style.SUCCESS('Теги загружены.'))
