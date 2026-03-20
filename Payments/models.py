import uuid
from django.db import models

class Payment(models.Model):
    # No ForeignKey to User
    email = models.EmailField()
    amount = models.PositiveIntegerField() # Kobo
    reference = models.CharField(max_length=100, unique=True, default=uuid.uuid4)
    verified = models.BooleanField(default=False)
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)