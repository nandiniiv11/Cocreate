from django.contrib import admin
from .models import Category, Idea

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Idea)
class IdeaAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'created_at')
    list_filter = ('categories', 'created_at')
    search_fields = ('title', 'description', 'created_by__username')
    date_hierarchy = 'created_at'
