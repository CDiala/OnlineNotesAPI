from django.contrib import admin

# Register your models here.


class NotesAdmin(admin.ModelAdmin):
    """
    Configure slug generation from title field
    """
    prepopulated_fields = {'slug': ['title']}
