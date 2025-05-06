from django.db import models

from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=50)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Categories"

class Idea(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    categories = models.ManyToManyField(Category, related_name='ideas')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ideas')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    collaborators = models.ManyToManyField(User, related_name='collaborated_ideas', blank=True)
    max_collaborators = models.IntegerField(default=3)

    def __str__(self):
        return self.title

    
    def __str__(self):
        return self.title
    
class CollaborationRequest(models.Model):
    idea    = models.ForeignKey(Idea, on_delete=models.CASCADE)
    sender  = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_requests')
    receiver= models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_requests')
    status  = models.CharField(max_length=10, choices=[('pending','Pending'),('accepted','Accepted')])
    created = models.DateTimeField(auto_now_add=True)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True)
    department = models.CharField(max_length=100, blank=True)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    resume_link = models.URLField(blank=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.user.username
    
class JoinRequest(models.Model):
    idea = models.ForeignKey(Idea, on_delete=models.CASCADE, related_name='join_requests')
    applicant = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{self.applicant} requested to join {self.idea}'
    
    