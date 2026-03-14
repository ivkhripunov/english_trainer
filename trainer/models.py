"""Models for the English trainer application."""
from django.db import models
from django.core.validators import MinLengthValidator


class Word(models.Model):
    """Represents an English word with its Russian translation."""

    english = models.CharField(
        max_length=200,
        validators=[MinLengthValidator(2)],
        verbose_name='English word',
    )
    russian = models.CharField(
        max_length=200,
        validators=[MinLengthValidator(2)],
        verbose_name='Russian translation',
    )
    example = models.TextField(
        blank=True,
        verbose_name='Example sentence',
    )
    times_shown = models.PositiveIntegerField(default=0)
    times_correct = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Meta options for Word model."""

        ordering = ['-created_at']
        verbose_name = 'Word'
        verbose_name_plural = 'Words'

    def __str__(self):
        """Return string representation."""
        return f"{self.english} — {self.russian}"

    @property
    def accuracy(self):
        """Calculate accuracy percentage for this word."""
        if self.times_shown == 0:
            return 0
        return round(self.times_correct / self.times_shown * 100)

    @property
    def accuracy_color(self):
        """Return Bootstrap color class based on accuracy."""
        acc = self.accuracy
        if acc >= 80:
            return 'success'
        if acc >= 50:
            return 'warning'
        return 'danger'
