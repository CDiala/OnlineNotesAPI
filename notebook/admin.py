from django.contrib import admin
from . import models


@admin.register(models.Note)
class NotebookAdmin(admin.ModelAdmin):
    '''
    Customizing the notes page in admin portal 
    '''
    list_display = [
        'owner',
        'title',
        'content',
        'slug',
        'created_at',
        'due_date',
        'priority',
        'status',
        'category'
    ]
    list_editable = ['content', 'status', 'priority', 'category', 'due_date']
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
        'is_email_valid',
        'created_at',
        'updated_at'
    ]
    list_select_related = ['user']


# Register your models here.
admin.site.register(models.Owner, OwnersAdmin)
