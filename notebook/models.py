from django.db import models
# from django.contrib.auth.models import User


class Owner(models.Model):
    '''
    Custom owner model that returns a concatenation 
    of first name and last name.
    '''
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    is_email_valid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f'{self.first_name} {self.last_name}'

    class Meta:
        ordering = ['email']


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
    slug = models.SlugField()
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
