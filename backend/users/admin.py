from django.contrib.admin import ModelAdmin, register, site

from .models import User, Follow


@register(User)
class UserAdmin(ModelAdmin):
    list_display = (
        'id',
        'username',
        'first_name',
        'last_name',
        'email',
    )
    list_filter = (
        'email',
        'username',
    )


@register(Follow)
class FollowAdmin(ModelAdmin):
    list_display = (
        'id',
        'author_id',
        'author',
        'user_id',
        'user',
    )


site.empty_value_display = 'Не задано'
