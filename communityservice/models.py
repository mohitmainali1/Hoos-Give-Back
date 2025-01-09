from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now
from django.conf import settings
from datetime import date
from django.core.exceptions import ValidationError

class CustomUser(AbstractUser):
    is_site_admin = models.BooleanField(default=False)
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)
    interests = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.first_name

class Project(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    time_of_creation = models.DateTimeField(default=now)
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="owned_projects")
    collaborators = models.ManyToManyField(CustomUser, related_name="collaborations", blank=True)
    project_date = models.DateField(default=date.today)  # will have corresponding date picker
    start_time = models.TimeField(default='09:00')  # will have a drop-down menu
    end_time = models.TimeField(default='17:00')  # will have a drop-down menu

    def __str__(self):
        return self.title

    def clean(self):  # makes sure that start time comes before end time
        if self.start_time >= self.end_time:
            raise ValidationError("Start time must be before end time.")

class JoinRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('denied', 'Denied'),
    ]

    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
    project = models.ForeignKey('Project', on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.first_name} - {self.project.title} ({self.status})"

class Document(models.Model):
    project = models.ForeignKey('Project', on_delete=models.CASCADE, related_name='documents')
    uploader = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, default="Untitled")
    keywords = models.TextField(blank=True, null=True, help_text='Enter keywords separated by commas')
    file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Task(models.Model):
    project = models.ForeignKey('Project', on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title