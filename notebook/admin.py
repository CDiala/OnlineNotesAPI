from django.contrib import admin
from . import models


@admin.register(models.Note)
class NotebookAdmin(admin.ModelAdmin):
    '''
    Customizing the notes page in admin portal 
    '''
    list_display = [
        'title',
        'content',
        'slug',
        'created_at',
        'due_date',
        'priority',
        'status',
        'category'
    ]
    list_editable = ['content', 'status', 'priority', 'category']
    list_per_page = 20

    """
    Configure slug generation from title field
    """
    prepopulated_fields = {'slug': ['title']}


class OwnersAdmin(admin.ModelAdmin):
    '''
    Customizing the owners page in admin portal 
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
    # list_editable = ['email']


# Register your models here.
admin.site.register(models.Owner, OwnersAdmin)
