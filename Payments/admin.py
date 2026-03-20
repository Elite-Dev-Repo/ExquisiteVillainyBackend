from django.contrib import admin
from .models import Payment
from Pass.models import Pass

# Register your models here.

admin.site.register(Payment)
admin.site.register(Pass)
