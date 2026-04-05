"""Admin configuration for the trainer application."""
from django.contrib import admin
from .models import Word, Collection, Language


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    """Admin interface for Language model."""

    list_display = ['name', 'native_name']
    search_fields = ['name']


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    """Admin interface for Collection model."""

    list_display = ['name', 'language', 'word_count', 'created_at']
    list_filter = ['language']
    search_fields = ['name']


@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    """Admin interface for Word model."""

    list_display = ['original', 'translation', 'collection', 'times_shown', 'times_correct']
    list_filter = ['collection__language', 'collection']
    search_fields = ['original', 'translation']
    readonly_fields = ['times_shown', 'times_correct', 'created_at']
