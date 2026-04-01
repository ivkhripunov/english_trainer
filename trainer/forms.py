"""Forms for the English trainer application."""
from django import forms
from .models import Word, Collection, Language

ALLOWED_ORIGINAL_CHARS = set(
    'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    'àáâãäåæçèéêëìíîïðñòóôõöùúûüýþÿ'
    'äöüßÄÖÜ'
    'àâæçéèêëîïôœùûüÿ'
    ' \'-'
)


class LanguageForm(forms.ModelForm):
    """Form for creating a new language."""

    class Meta:
        """Meta options for LanguageForm."""

        model = Language
        fields = ['name', 'native_name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Spanish',
                'autocomplete': 'off',
            }),
            'native_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Español',
                'autocomplete': 'off',
            }),
        }
        labels = {
            'name': 'Language name (in English)',
            'native_name': 'Name in native language (optional)',
        }

    def clean_name(self):
        """Validate language name."""
        value = self.cleaned_data.get('name', '').strip()
        if not value:
            raise forms.ValidationError('Please enter a language name.')
        if len(value) < 2:
            raise forms.ValidationError('Name must be at least 2 characters.')
        return value.capitalize()


class CollectionForm(forms.ModelForm):
    """Form for creating and editing a word collection."""

    class Meta:
        """Meta options for CollectionForm."""

        model = Collection
        fields = ['name', 'description', 'language']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Advanced Vocabulary',
                'autocomplete': 'off',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Short description of this collection...',
            }),
            'language': forms.Select(attrs={
                'class': 'form-select',
            }),
        }
        labels = {
            'name': 'Collection name',
            'description': 'Description (optional)',
            'language': 'Language',
        }

    def clean_name(self):
        """Validate collection name."""
        value = self.cleaned_data.get('name', '').strip()
        if not value:
            raise forms.ValidationError('Please enter a collection name.')
        if len(value) < 2:
            raise forms.ValidationError('Name must be at least 2 characters.')
        if len(value) > 200:
            raise forms.ValidationError('Name must not exceed 200 characters.')
        return value


class WordForm(forms.ModelForm):
    """Form for creating and editing vocabulary words."""

    class Meta:
        """Meta options for WordForm."""

        model = Word
        fields = ['original', 'translation', 'example', 'collection']
        widgets = {
            'original': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. perseverance',
                'autocomplete': 'off',
            }),
            'translation': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. настойчивость',
                'autocomplete': 'off',
            }),
            'example': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'e.g. Her perseverance paid off in the end.',
            }),
            'collection': forms.Select(attrs={
                'class': 'form-select',
            }),
        }
        labels = {
            'original': 'Word / phrase (original)',
            'translation': 'Translation (Russian)',
            'example': 'Example sentence (optional)',
            'collection': 'Collection (optional)',
        }

    def clean_original(self):
        """Validate the original word field."""
        value = self.cleaned_data.get('original', '').strip()
        if not value:
            raise forms.ValidationError('Please enter the original word.')
        if len(value) < 2:
            raise forms.ValidationError('Word must be at least 2 characters.')
        if len(value) > 200:
            raise forms.ValidationError('Word must not exceed 200 characters.')
        return value.lower()

    def clean_translation(self):
        """Validate the translation field."""
        value = self.cleaned_data.get('translation', '').strip()
        if not value:
            raise forms.ValidationError('Please enter a translation.')
        if len(value) < 2:
            raise forms.ValidationError('Translation must be at least 2 characters.')
        if len(value) > 200:
            raise forms.ValidationError('Translation must not exceed 200 characters.')
        return value.lower()

    def clean_example(self):
        """Validate the example sentence field."""
        value = self.cleaned_data.get('example', '').strip()
        if value and len(value) > 500:
            raise forms.ValidationError('Example must not exceed 500 characters.')
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
        ('orig_trans', 'Original → Translation'),
        ('trans_orig', 'Translation → Original'),
    ]

    collection = forms.ModelChoiceField(
        queryset=Collection.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Collection',
        empty_label='— All words —',
        required=False,
    )
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

    def __init__(self, *args, **kwargs):
        """Populate the collection queryset dynamically."""
        super().__init__(*args, **kwargs)
        self.fields['collection'].queryset = Collection.objects.select_related('language')
