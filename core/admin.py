from django.contrib import admin
from . import models

# Register your models here.


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'first_name',
        'last_name',
        'email',
        'is_active',
        'is_superuser'
    )


admin.site.register(models.User, UserAdmin)
