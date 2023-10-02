from django.db import models
from django.contrib.auth.models import User


class Note(models.Model):
    """
    This note model includes fields for the user who created the note, 
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

    user = models.ForeignKey(User, on_delete=models.CASCADE)
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

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
