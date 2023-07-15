from django.contrib import admin
from .models import MyUser, Address


# Register your models here.
admin.site.register([MyUser, Address])
