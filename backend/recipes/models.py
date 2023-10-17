from django.db import models

from users.models import User


class Recipe(models.Model):
    """Модель рецептов."""

    name = models.CharField(
        max_length=200,
        verbose_name='Название',
        help_text='Введите название рецепта',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
        help_text='Выберите автора',
    )
    image = models.ImageField(
        upload_to='recipes/images',
        default=None,
        verbose_name='Фото блюда',
        help_text='Выберите изображение',
    )
    text = models.TextField(
        verbose_name='Описание',
        help_text='Укажите способ приготовления',
    )
    ingredients = models.ManyToManyField(
        'Ingredient',
        through='RecipeIngredients',
        blank=True,
        related_name='recipes',
        verbose_name='Ингредиенты',
        help_text='Выберите ингредиенты',
    )
    tags = models.ManyToManyField(
        'Tag',
        through='RecipeTags',
        related_name='recipes',
        verbose_name='Тег',
        help_text='Выберите тег или создайте новый',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        help_text='Укажите значение в минутах',

    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
        help_text='Дата публикации',
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
        verbose_name='Ингредиент',
        help_text='Введите название ингредиента',
    )
    measurement_unit = models.CharField(
        max_length=50,
        verbose_name='Единицв измерения',
        help_text='Введите единицу измерения',
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return self.name


class RecipeIngredients(models.Model):
    """Модель связи ингредиентов с рецептами."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
    )
    amount = models.PositiveSmallIntegerField(
        null=True,
        verbose_name='Количество',
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        models.UniqueConstraint(
            fields=['recipe', 'ingredient'],
            name='unique_ingredient',
        )

    def __str__(self):
        return f'Ингредиент {self.ingredient} в рецепте {self.recipe}'


class Tag(models.Model):
    """Модель тегов."""

    name = models.CharField(
        max_length=200,
        verbose_name='Название',
        help_text='Введите название тега',
    )
    color = models.CharField(
        max_length=7,
        unique=True,
        verbose_name='Цвет',
        help_text='Введите цвет в HEX формате (#000000)',
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name='Слаг',
        help_text='Введите слаг',
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class RecipeTags(models.Model):
    """Модель связи тегов с рецептами."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        help_text='Введите id рецепта',
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        verbose_name='Тег',
        help_text='Введите id тега',
    )

    class Meta:
        verbose_name = 'Тег рецепта'
        verbose_name_plural = 'Теги рецептов'
        models.UniqueConstraint(
            fields=['recipe', 'tag'],
            name='unique_tag',
        )

    def __str__(self):
        return f'Тег {self.tag} в рецепте {self.recipe}'


class Favorite(models.Model):
    """Модель избранного."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite',
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

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shoppingcart',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shoppingcart',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        models.UniqueConstraint(
            fields=['user', 'recipe'],
            name='unique_shopping_cart',
        )

    def __str__(self):
        return (f'{self.recipe} в списке покупок у пользователя '
                f'{self.user.first_name} {self.user.last_name}')
