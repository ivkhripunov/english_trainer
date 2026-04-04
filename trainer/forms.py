"""Forms for the English trainer application."""
from django import forms
from .models import Word, Collection, Language


class LanguageForm(forms.ModelForm):
    """Form for creating a new language."""

    class Meta:
        """Meta options for LanguageForm."""

        model = Language
        fields = ['name', 'native_name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'напр. Английский',
                'autocomplete': 'off',
            }),
            'native_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'напр. English',
                'autocomplete': 'off',
            }),
        }
        labels = {
            'name': 'Название языка (на русском)',
            'native_name': 'Название на родном языке (необязательно)',
        }

    def clean_name(self):
        """Validate language name."""
        value = self.cleaned_data.get('name', '').strip()
        if not value:
            raise forms.ValidationError('Введите название языка.')
        if len(value) < 2:
            raise forms.ValidationError('Название должно быть не короче 2 символов.')
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
                'placeholder': 'напр. Продвинутая лексика',
                'autocomplete': 'off',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Краткое описание подборки...',
            }),
            'language': forms.Select(attrs={
                'class': 'form-select',
            }),
        }
        labels = {
            'name': 'Название подборки',
            'description': 'Описание (необязательно)',
            'language': 'Язык',
        }

    def clean_name(self):
        """Validate collection name."""
        value = self.cleaned_data.get('name', '').strip()
        if not value:
            raise forms.ValidationError('Введите название подборки.')
        if len(value) < 2:
            raise forms.ValidationError('Название должно быть не короче 2 символов.')
        if len(value) > 200:
            raise forms.ValidationError('Название не должно превышать 200 символов.')
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
                'placeholder': 'напр. perseverance',
                'autocomplete': 'off',
            }),
            'translation': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'напр. настойчивость',
                'autocomplete': 'off',
            }),
            'example': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'напр. Her perseverance paid off in the end.',
            }),
            'collection': forms.Select(attrs={
                'class': 'form-select',
            }),
        }
        labels = {
            'original': 'Слово / фраза (оригинал)',
            'translation': 'Перевод (на русском)',
            'example': 'Пример предложения (необязательно)',
            'collection': 'Подборка (необязательно)',
        }

    def clean_original(self):
        """Validate the original word field."""
        value = self.cleaned_data.get('original', '').strip()
        if not value:
            raise forms.ValidationError('Введите слово на изучаемом языке.')
        if len(value) < 2:
            raise forms.ValidationError('Слово должно содержать не менее 2 символов.')
        if len(value) > 200:
            raise forms.ValidationError('Слово не должно превышать 200 символов.')
        return value.lower()

    def clean_translation(self):
        """Validate the translation field."""
        value = self.cleaned_data.get('translation', '').strip()
        if not value:
            raise forms.ValidationError('Введите перевод слова.')
        if len(value) < 2:
            raise forms.ValidationError('Перевод должен содержать не менее 2 символов.')
        if len(value) > 200:
            raise forms.ValidationError('Перевод не должен превышать 200 символов.')
        return value.lower()

    def clean_example(self):
        """Validate the example sentence field."""
        value = self.cleaned_data.get('example', '').strip()
        if value and len(value) > 500:
            raise forms.ValidationError('Пример не должен превышать 500 символов.')
        return value


class QuizAnswerForm(forms.Form):
    """Form for submitting a quiz answer."""

    answer = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg text-center',
            'placeholder': 'Введите ответ...',
            'autocomplete': 'off',
            'autofocus': True,
        }),
        label='',
    )

    def clean_answer(self):
        """Validate and normalise the answer."""
        value = self.cleaned_data.get('answer', '').strip()
        if not value:
            raise forms.ValidationError('Введите ответ перед отправкой.')
        return value.lower()


class QuizSettingsForm(forms.Form):
    """Form for configuring quiz parameters."""

    COUNT_CHOICES = [
        (5, '5 слов'),
        (10, '10 слов'),
        (20, '20 слов'),
        (0, 'Все слова'),
    ]
    DIRECTION_CHOICES = [
        ('orig_trans', 'Оригинал → Перевод'),
        ('trans_orig', 'Перевод → Оригинал'),
    ]

    collection = forms.ModelChoiceField(
        queryset=Collection.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Подборка',
        empty_label='— Все слова —',
        required=False,
    )
    count = forms.ChoiceField(
        choices=COUNT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Количество слов',
        initial=10,
    )
    direction = forms.ChoiceField(
        choices=DIRECTION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Направление перевода',
    )

    def __init__(self, *args, **kwargs):
        """Populate the collection queryset dynamically."""
        super().__init__(*args, **kwargs)
        self.fields['collection'].queryset = Collection.objects.select_related('language')
