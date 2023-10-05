# from django.core.validators import validate_slug
from django.db import models

from users.models import User

# from .validators import (
#     validate_score, validate_username, validate_username_bad_sign,
#     validate_year,
# )


# User = get_user_model()


class Recipe(models.Model):
    """Модель рецептов."""

    name = models.CharField(
        max_length=200,
        help_text='Введите название рецепта',
        verbose_name='Рецепт'
    )
    author = models.ForeignKey(
        to='User',
        on_delete=models.CASCADE,
        related_name='recipe',
        verbose_name='Автор',
    )
    image = models.ImageField(
        upload_to='recipes/images',
        default=None,
        verbose_name='Фото блюда',
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
    )
    ingredients = models.ManyToManyField(
        to='Ingredient',
        through='RecipeIngredients',
        verbose_name='Ингредиенты',
    )
    tags = models.ManyToManyField(
        to='Tag',
        related_name='recipe',
        verbose_name='Тег',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления (в минутах)',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингредиентов."""

    name = models.CharField(
        max_length=100,
    )
    measurement_unit = models.CharField(
        max_length=50,
        verbose_name='Единица измерения',
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class RecipeIngredients(models.Model):
    """Модель ингредиентов в рецепте."""

    recipe = models.ForeignKey(
        to='Recipe',
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        to='Ingredient',
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество'
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        unique_together = ('recipe', 'ingredient')

    def __str__(self):
        return f'Ингредиент {self.ingredient} в рецепте {self.recipe}'


class Tag(models.Model):
    """Модель тегов."""

    name = models.CharField(
        max_length=200,
        verbose_name='Тэг',
    )
    color = models.CharField(
        max_length=7,
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class RecipeTags(models.Model):
    """Модель тегов рецепта."""

    recipe = models.ForeignKey(
        to='Recipe',
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )
    tag = models.ForeignKey(
        to='Tag',
        on_delete=models.CASCADE,
        verbose_name='Тег',
    )

    class Meta:
        verbose_name = 'Тег рецепта.'
        verbose_name_plural = 'Теги рецептов.'
        unique_together = ('recipe', 'tag')

    def __str__(self):
        return f'Тег {self.tag} в рецепте {self.recipe}'


class Favorite(models.Model):
    """Модель избранного."""

    user = models.ForeignKey(
        to='User',
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        to='Recipe',
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        models.UniqueConstraint(
            fields=['user', 'recipe'],
            name='unique_favorite',
        )

    def __str__(self):
        return f'Рецепт {self.recipe} в избранном у пользователя {self.user}'


class ShoppingCart(models.Model):
    """Модель списка покупок."""

    recipe = models.ForeignKey(
        to='Recipe',
        on_delete=models.CASCADE,
        related_name='shoppingcart',
        verbose_name='Рецепт',
    )
    user = models.ForeignKey(
        to='User',
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь',
    )
    when_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-when_added']
        verbose_name = 'Список покупок'
        verbose_name_plural = verbose_name
        unique_together = ('user', 'recipe')

    def __str__(self):
        return f'{self.user} added {self.recipe}'


# ##################################
#
#
#
#
# class Review(models.Model):
#     """Модель отзывов."""
#
#     title = models.ForeignKey(
#         'Title',
#         on_delete=models.CASCADE,
#         related_name='reviews',
#         verbose_name='Произведение',
#     )
#     text = models.TextField(
#         help_text='Введите текст отзыва',
#         verbose_name='Текст отзыва',
#     )
#     author = models.ForeignKey(
#         User,
#         on_delete=models.CASCADE,
#         related_name='reviews',
#         verbose_name='Автор',
#     )
#     score = models.IntegerField(
#         help_text='Поставьте вашу оценку от 1 до 10',
#         verbose_name='Оценка',
#         validators=[validate_score],
#         default=0,
#     )
#     pub_date = models.DateTimeField(
#         auto_now_add=True, verbose_name='Дата публикации'
#     )
#
#     class Meta:
#         ordering = ('-pub_date',)
#         verbose_name = 'Отзыв'
#         verbose_name_plural = 'Отзывы'
#         constraints = [
#             models.UniqueConstraint(
#                 fields=['author', 'title'], name='unique_author_title'
#             )
#         ]
#
#     def __str__(self):
#         return self.text[:15]
#
#
# class Comment(models.Model):
#     """Модель комментариев."""
#
#     review = models.ForeignKey(
#         Review,
#         on_delete=models.CASCADE,
#         related_name='comments',
#         verbose_name='Комментарий',
#     )
#     text = models.TextField(
#         help_text='Напишите ваш комментарий', verbose_name='Комментарий'
#     )
#     author = models.ForeignKey(
#         User,
#         on_delete=models.CASCADE,
#         related_name='comments',
#         verbose_name='Автор',
#     )
#
#     pub_date = models.DateTimeField(
#         auto_now_add=True, db_index=True, verbose_name='Дата публикации'
#     )
#
#     class Meta:
#         ordering = ('-pub_date',)
#         verbose_name = 'Комментарий'
#         verbose_name_plural = 'Комментарии'
#
#     def __str__(self):
#         return self.text[:15]
#
#
# class Genre(models.Model):
#     """Модель жанров."""
#
#     name = models.CharField('Жанр', max_length=MAX_LENGTH_GENRE_NAME)
#     slug = models.SlugField(
#         'Слаг',
#         unique=True,
#         max_length=MAX_LENGTH_GENRE_SLUG,
#         validators=[validate_slug],
#     )
#
#     class Meta:
#         ordering = ('name',)
#         verbose_name = 'Жанр'
#         verbose_name_plural = 'Жанры'
#
#     def __str__(self):
#         return self.name
#
#
# class Category(models.Model):
#     """Модель категорий."""
#
#     name = models.CharField('Категория', max_length=MAX_LENGTH_CATEGORY_NAME)
#     slug = models.SlugField(
#         'Слаг',
#         unique=True,
#         max_length=MAX_LENGTH_CATEGORY_SLUG,
#         validators=[validate_slug],
#     )
#
#     class Meta:
#         ordering = ('name',)
#         verbose_name = 'Категория'
#         verbose_name_plural = 'Категории'
#
#     def __str__(self):
#         return self.name
#
#
# class Title(models.Model):
#     """Модель произведений."""
#
#     name = models.CharField(
#         max_length=MAX_LENGTH_TITLE_NAME, verbose_name='Произведение'
#     )
#     year = models.PositiveSmallIntegerField(
#         validators=[validate_year],
#     )
#     category = models.ForeignKey(
#         Category, related_name='titles', on_delete=models.SET_NULL, null=True
#     )
#     genre = models.ManyToManyField(
#         Genre,
#         related_name='titles',
#         through='GenreTitle',
#     )
#     description = models.TextField(blank=True, verbose_name='Описание')
#
#     class Meta:
#         ordering = ('name',)
#         verbose_name = 'Произведение'
#         verbose_name_plural = 'Произведения'
#
#     def __str__(self):
#         return self.name
#
#
# class GenreTitle(models.Model):
#     """Связь жанров и произведений."""
#
#     genre = models.ForeignKey(Genre, on_delete=models.PROTECT)
#     title = models.ForeignKey(Title, on_delete=models.CASCADE)
