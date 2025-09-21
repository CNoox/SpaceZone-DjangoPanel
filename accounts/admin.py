from django.contrib import admin
from .models import CustomUserModel,UserCodeModel

# Register your models here.

admin.site.register(UserCodeModel)

@admin.register(CustomUserModel)
class CustomUserModelAdmin(admin.ModelAdmin):
    list_display = ('email','is_staff','is_superuser')
    list_filter = ('is_staff','is_superuser')
