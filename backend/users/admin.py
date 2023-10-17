from django.contrib.admin import ModelAdmin, register, site

from .models import User, Follow


@register(User)
class UserAdmin(ModelAdmin):
    list_display = (
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
        'author',
        'user',
    )


site.empty_value_display = 'Не задано'
