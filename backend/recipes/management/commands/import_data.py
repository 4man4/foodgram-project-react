import json
from django.core.management.base import BaseCommand

from recipes.models import Ingredient, Tag


class Command(BaseCommand):
    help = 'Импорт данных в БД'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Начало импорта'))
        with open(
            '../data/ingredients.json',
            encoding='utf-8',
        ) as file_data_ingredients:
            ingredient_data = json.loads(file_data_ingredients.read())
            for ingredients in ingredient_data:
                Ingredient.objects.get_or_create(**ingredients)

        with open(
            '../data/tags.json',
            encoding='utf-8',
        ) as file_data_tags:
            tags_data = json.loads(file_data_tags.read())
            for tags in tags_data:
                Tag.objects.get_or_create(**tags)

        self.stdout.write(self.style.SUCCESS('Конец импорта'))