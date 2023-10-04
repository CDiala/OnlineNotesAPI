from django.contrib import admin
from . import models


class UsersAdmin(admin.ModelAdmin):
    '''
    Customizing the user page in admin portal 
    '''

    list_display = [
        'first_name',
        'last_name',
        'email',
        'password',
        'is_email_valid',
        'created_at',
        'updated_at'
    ]
    list_editable = ['email']


# Register your models here.
admin.site.register(models.User, UsersAdmin)
