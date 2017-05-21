from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(Category)
admin.site.register(Url)
admin.site.register(Label)
admin.site.register(Citation)
admin.site.register(User)
admin.site.register(SavedUrl)

