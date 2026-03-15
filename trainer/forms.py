"""Forms for the English trainer application."""
from django import forms
from .models import Word

ALLOWED_ENGLISH_CHARS = set(
    'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ \'-'
)


class WordForm(forms.ModelForm):
    """Form for creating and editing vocabulary words."""

    class Meta:
        """Meta options for WordForm."""

        model = Word
        fields = ['english', 'russian', 'example']
        widgets = {
            'english': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. perseverance',
                'autocomplete': 'off',
            }),
            'russian': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. настойчивость',
                'autocomplete': 'off',
            }),
            'example': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'e.g. Her perseverance paid off in the end.',
            }),
        }
        labels = {
            'english': 'English word / phrase',
            'russian': 'Russian translation',
            'example': 'Example sentence (optional)',
        }

    def clean_english(self):
        """Validate the English word field."""
        value = self.cleaned_data.get('english', '').strip()
        if not value:
            raise forms.ValidationError('Please enter an English word.')
        if len(value) < 2:
            raise forms.ValidationError(
                'The word must be at least 2 characters long.'
            )
        if len(value) > 200:
            raise forms.ValidationError(
                'The word must not exceed 200 characters.'
            )
        if not all(c in ALLOWED_ENGLISH_CHARS for c in value):
            raise forms.ValidationError(
                'Only letters, spaces, hyphens and apostrophes are allowed.'
            )
        return value.lower()

    def clean_russian(self):
        """Validate the Russian translation field."""
        value = self.cleaned_data.get('russian', '').strip()
        if not value:
            raise forms.ValidationError('Please enter a Russian translation.')
        if len(value) < 2:
            raise forms.ValidationError(
                'The translation must be at least 2 characters long.'
            )
        if len(value) > 200:
            raise forms.ValidationError(
                'The translation must not exceed 200 characters.'
            )
        return value.lower()

    def clean_example(self):
        """Validate the example sentence field."""
        value = self.cleaned_data.get('example', '').strip()
        if value and len(value) > 500:
            raise forms.ValidationError(
                'Example sentence must not exceed 500 characters.'
            )
        return value


class QuizAnswerForm(forms.Form):
    """Form for submitting a quiz answer."""

    answer = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg text-center',
            'placeholder': 'Type your answer here...',
            'autocomplete': 'off',
            'autofocus': True,
        }),
        label='',
    )

    def clean_answer(self):
        """Validate and normalise the answer."""
        value = self.cleaned_data.get('answer', '').strip()
        if not value:
            raise forms.ValidationError('Please type an answer before submitting.')
        return value.lower()


class QuizSettingsForm(forms.Form):
    """Form for configuring quiz parameters."""

    COUNT_CHOICES = [
        (5, '5 words'),
        (10, '10 words'),
        (20, '20 words'),
        (0, 'All words'),
    ]
    DIRECTION_CHOICES = [
        ('en_ru', 'English → Russian'),
        ('ru_en', 'Russian → English'),
    ]

    count = forms.ChoiceField(
        choices=COUNT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Number of words',
        initial=10,
    )
    direction = forms.ChoiceField(
        choices=DIRECTION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Quiz direction',
    )
