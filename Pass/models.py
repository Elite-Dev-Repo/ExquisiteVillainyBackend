# Pass/models.py
from django.db import models
from Payments.models import Payment # Import your Payment model

class Pass(models.Model):
    email = models.EmailField()
    pass_code = models.CharField(max_length=200, unique=True)
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='generated_pass', null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.email} - {self.pass_code}"