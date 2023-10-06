from django.contrib import admin
from django.db import models
from django.conf import settings


class Owner(models.Model):
    '''
    Custom owner model that returns a concatenation 
    of first name and last name.
    '''
    is_email_valid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f'{self.user.first_name} {self.user.last_name}'

    @admin.display(ordering='user__first_name')
    def first_name(self):
        return self.user.first_name

    @admin.display(ordering='user__last_name')
    def last_name(self):
        return self.user.last_name

    def email(self):
        return self.user.email

    class Meta:
        ordering = ['user__email']


class Note(models.Model):
    """
    This model includes fields for the owner who created the note, 
    a title, content, priority, status, due date, and timestamps for 
    when the note was created and last updated. It also has predefined 
    priority and status choices. List of notes are generated and ordered 
    from most recently created.
    """
    PRIORITY_LOW = 'L'
    PRIORITY_MEDIUM = 'M'
    PRIORITY_HIGH = 'H'
    PRIORITY_CHOICES = [
        (PRIORITY_LOW, "Low"),
        (PRIORITY_MEDIUM, "Medium"),
        (PRIORITY_HIGH, "High")
    ]

    STATUS_NEW = 'N'
    STATUS_WIP = 'P'
    STATUS_END = 'C'
    STATUS_DEL = 'D'
    STATUS_CHOICES = [
        (STATUS_NEW, 'New'),
        (STATUS_WIP, "In Progress"),
        (STATUS_END, "Completed"),
        (STATUS_DEL, "Deleted")
    ]

    CATEGORY_NONE = 'N'
    CATEGORY_BLUE = 'B'
    CATEGORY_GREEN = 'G'
    CATEGORY_ORANGE = 'O'
    CATEGORY_PURPLE = 'P'
    CATEGORY_RED = 'R'
    CATEGORY_YELLOW = 'Y'
    CATEGORY_CHOICES = [
        (CATEGORY_NONE, 'None'),
        (CATEGORY_BLUE, 'Blue'),
        (CATEGORY_GREEN, 'Green'),
        (CATEGORY_ORANGE, 'Orange'),
        (CATEGORY_PURPLE, 'Purple'),
        (CATEGORY_RED, 'Red'),
        (CATEGORY_YELLOW, 'Yellow'),
    ]

    owner = models.ForeignKey(Owner, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    content = models.TextField()
    slug = models.SlugField(null=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    due_date = models.DateField(null=True, blank=True)
    priority = models.CharField(
        max_length=1, choices=PRIORITY_CHOICES, default=PRIORITY_MEDIUM)
    status = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default=STATUS_NEW)
    category = models.CharField(
        max_length=1, choices=CATEGORY_CHOICES, default=CATEGORY_NONE)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
