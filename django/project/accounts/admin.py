from django.contrib import admin

# Register your models here.

from .models import *

admin.site.register(employee)
admin.site.register(access)
admin.site.register(history)
