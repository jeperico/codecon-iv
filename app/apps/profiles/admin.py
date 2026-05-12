from django.contrib import admin
from .models import User


class UserAdmin(admin.ModelAdmin):
  list_display = ['id', 'name', 'email', 'created_at', 'updated_at']
  search_fields = ['name', 'email']
  list_filter = ['created_at', 'updated_at']
  readonly_fields = ['created_at', 'updated_at']

admin.site.register(User, UserAdmin)
