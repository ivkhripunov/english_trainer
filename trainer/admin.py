"""Admin configuration for the trainer application."""
from django.contrib import admin
from .models import Word


@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    """Admin interface for Word model."""

    list_display = ['english', 'russian', 'times_shown', 'times_correct', 'created_at']
    list_filter = ['created_at']
    search_fields = ['english', 'russian']
    readonly_fields = ['times_shown', 'times_correct', 'created_at']
