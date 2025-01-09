from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

# Customizing the admin interface for the CustomUser model
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('is_site_admin',)}),
    )
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_site_admin']

admin.site.register(CustomUser, CustomUserAdmin)

# Registering the Project model
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title'),
    search_fields = ('title',)
    filter_horizontal = ('collaborators',)

# Registering the Document model
@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_at', 'project', 'uploader')
    search_fields = ('title', 'keywords')
    list_filter = ('uploaded_at', 'project')
    readonly_fields = ('uploaded_at',)