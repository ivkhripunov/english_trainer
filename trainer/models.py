"""Models for the English trainer application."""
from django.db import models
from django.core.validators import MinLengthValidator


class Language(models.Model):
    """Represents a language available for study."""

    name = models.CharField(
        max_length=100,
        unique=True,
        validators=[MinLengthValidator(2)],
        verbose_name='Language name',
    )
    native_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Name in native language',
    )

    class Meta:
        """Meta options for Language model."""

        ordering = ['name']
        verbose_name = 'Language'
        verbose_name_plural = 'Languages'

    def __str__(self):
        """Return string representation."""
        return self.name

    @property
    def word_count(self):
        """Return total word count across all collections for this language."""
        return Word.objects.filter(collection__language=self).count()

    @property
    def collection_count(self):
        """Return number of collections for this language."""
        return self.collections.count()


class Collection(models.Model):
    """A named set of words for a particular language."""

    name = models.CharField(
        max_length=200,
        validators=[MinLengthValidator(2)],
        verbose_name='Collection name',
    )
    description = models.TextField(
        blank=True,
        verbose_name='Description',
    )
    language = models.ForeignKey(
        Language,
        on_delete=models.CASCADE,
        related_name='collections',
        verbose_name='Language',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Meta options for Collection model."""

        ordering = ['-created_at']
        verbose_name = 'Collection'
        verbose_name_plural = 'Collections'

    def __str__(self):
        """Return string representation."""
        return f"{self.name} [{self.language}]"

    @property
    def word_count(self):
        """Return number of words in this collection."""
        return self.words.count()

    @property
    def total_shown(self):
        """Return total times words in this collection were shown."""
        return sum(w.times_shown for w in self.words.all())

    @property
    def total_correct(self):
        """Return total correct answers for this collection."""
        return sum(w.times_correct for w in self.words.all())

    @property
    def accuracy(self):
        """Return overall accuracy percentage for this collection."""
        shown = self.total_shown
        if shown == 0:
            return 0
        return round(self.total_correct / shown * 100)

    @property
    def accuracy_color(self):
        """Return Bootstrap color class based on accuracy."""
        acc = self.accuracy
        if acc >= 80:
            return 'success'
        if acc >= 50:
            return 'warning'
        return 'danger'


class Word(models.Model):
    """Represents a word card within a collection."""

    collection = models.ForeignKey(
        Collection,
        on_delete=models.CASCADE,
        related_name='words',
        verbose_name='Collection',
        null=True,
        blank=True,
    )
    original = models.CharField(
        max_length=200,
        validators=[MinLengthValidator(2)],
        verbose_name='Original word',
    )
    translation = models.CharField(
        max_length=200,
        validators=[MinLengthValidator(2)],
        verbose_name='Translation (Russian)',
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
        return f"{self.original} — {self.translation}"

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
