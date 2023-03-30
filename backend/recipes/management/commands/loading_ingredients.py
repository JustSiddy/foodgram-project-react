from csv import reader

from django.core.management import BaseCommand

from recipes.models import Ingredient,  Tags


class Command(BaseCommand):
    help = 'Load ingredients data from csv-file to DB.'

    def handle(self, *args, **kwargs):
        with open(
                'recipes/data/ingredients.csv', 'r',
                encoding='UTF-8'
        ) as ingredients:
            for row in reader(ingredients):
                if len(row) == 2:
                    Ingredient.objects.get_or_create(
                        name=row[0], measurement_unit=row[1],
                    )
        self.stdout.write(self.style.SUCCESS('Ингредиенты загружены'))
        
        with open(
                'recipes/data/tags.csv', 'r',
                encoding='UTF-8'
        ) as tags:
            for row in reader(tags):
                if len(row) == 3:
                    Tags.objects.get_or_create(
                        name=row[0], color=row[1], slug=row[2],
                    )
        self.stdout.write(self.style.SUCCESS('Теги загружены'))
