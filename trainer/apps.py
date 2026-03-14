"""AppConfig for the trainer application."""
from django.apps import AppConfig


class TrainerConfig(AppConfig):
    """Configuration for the trainer app."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'trainer'
    verbose_name = 'English Trainer'
