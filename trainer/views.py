"""Views for the English trainer application."""
import json
import random
import urllib.request
import urllib.parse
import urllib.error
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse
from django.db.models import Q, Sum, F, FloatField, ExpressionWrapper

from .models import Word, Collection, Language, QuizResult
from .forms import (
    WordForm, QuizAnswerForm, QuizSettingsForm,
    CollectionForm, LanguageForm, RegisterForm,
)

MIN_WORDS_FOR_QUIZ = 1
API_TIMEOUT = 5


# ── Auth ──────────────────────────────────────────────────────────────────────

def register_view(request):
    """Handle user registration."""
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"🎉 Добро пожаловать, {user.username}!")
            return redirect('index')
    else:
        form = RegisterForm()

    return render(request, 'trainer/register.html', {'form': form})


def login_view(request):
    """Handle user login."""
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get('next', 'index')
            return redirect(next_url)
        messages.error(request, 'Неверное имя пользователя или пароль.')
    else:
        form = AuthenticationForm()

    form.fields['username'].widget.attrs.update({
        'class': 'form-control',
        'placeholder': 'Имя пользователя',
    })
    form.fields['password'].widget.attrs.update({
        'class': 'form-control',
        'placeholder': 'Пароль',
    })
    return render(request, 'trainer/login.html', {'form': form})


def logout_view(request):
    """Handle user logout."""
    if request.method == 'POST':
        logout(request)
        return redirect('login')
    return redirect('index')


# ── Home ──────────────────────────────────────────────────────────────────────

def index(request):
    """Render the home page with statistics for the current user."""
    if request.user.is_authenticated:
        word_qs = Word.objects.filter(collection__owner=request.user)
        collection_qs = Collection.objects.filter(owner=request.user)
    else:
        word_qs = Word.objects.all()
        collection_qs = Collection.objects.all()

    total_words = word_qs.count()
    total_collections = collection_qs.count()
    total_languages = Language.objects.count()
    recent_collections = collection_qs.select_related('language').order_by('-created_at')[:4]

    aggregates = word_qs.aggregate(
        total_shown=Sum('times_shown'),
        total_correct=Sum('times_correct'),
    )
    total_shown = aggregates['total_shown'] or 0
    total_correct = aggregates['total_correct'] or 0
    overall_accuracy = (
        round(total_correct / total_shown * 100) if total_shown > 0 else 0
    )

    hardest_words = (
        word_qs.filter(times_shown__gt=0)
        .select_related('collection__language')
        .annotate(
            accuracy_rate=ExpressionWrapper(
                F('times_correct') * 100.0 / F('times_shown'),
                output_field=FloatField(),
            )
        )
        .order_by('accuracy_rate')[:3]
    )

    context = {
        'total_words': total_words,
        'total_collections': total_collections,
        'total_languages': total_languages,
        'overall_accuracy': overall_accuracy,
        'total_shown': total_shown,
        'recent_collections': recent_collections,
        'hardest_words': hardest_words,
    }
    return render(request, 'trainer/index.html', context)


# ── Profile ───────────────────────────────────────────────────────────────────

@login_required
def profile(request):
    """Render the user profile page with learning statistics."""
    word_qs = Word.objects.filter(collection__owner=request.user)
    collection_qs = Collection.objects.filter(owner=request.user)
    quiz_qs = QuizResult.objects.filter(owner=request.user)

    total_words = word_qs.count()
    total_quizzes = quiz_qs.count()
    recent_quizzes = quiz_qs.select_related('collection__language')[:10]

    aggregates = word_qs.aggregate(
        total_shown=Sum('times_shown'),
        total_correct=Sum('times_correct'),
    )
    total_shown = aggregates['total_shown'] or 0
    total_correct = aggregates['total_correct'] or 0
    overall_accuracy = (
        round(total_correct / total_shown * 100) if total_shown > 0 else 0
    )

    quiz_aggregates = quiz_qs.aggregate(
        total_score=Sum('score'),
        total_questions=Sum('total'),
    )
    quiz_total_score = quiz_aggregates['total_score'] or 0
    quiz_total_questions = quiz_aggregates['total_questions'] or 0
    quiz_accuracy = (
        round(quiz_total_score / quiz_total_questions * 100)
        if quiz_total_questions > 0 else 0
    )

    best_collection = (
        collection_qs.filter(words__times_shown__gt=0)
        .annotate(
            acc=ExpressionWrapper(
                Sum('words__times_correct') * 100.0 / Sum('words__times_shown'),
                output_field=FloatField(),
            )
        )
        .order_by('-acc')
        .first()
    )

    hardest_collection = (
        collection_qs.filter(words__times_shown__gt=0)
        .annotate(
            acc=ExpressionWrapper(
                Sum('words__times_correct') * 100.0 / Sum('words__times_shown'),
                output_field=FloatField(),
            )
        )
        .order_by('acc')
        .first()
    )

    achievements = _get_achievements(total_words, total_quizzes, overall_accuracy)

    context = {
        'total_words': total_words,
        'total_quizzes': total_quizzes,
        'overall_accuracy': overall_accuracy,
        'quiz_accuracy': quiz_accuracy,
        'total_shown': total_shown,
        'recent_quizzes': recent_quizzes,
        'best_collection': best_collection,
        'hardest_collection': hardest_collection,
        'achievements': achievements,
    }
    return render(request, 'trainer/profile.html', context)


def _get_achievements(total_words, total_quizzes, accuracy):
    """Return list of earned achievement badges."""
    earned = []
    if total_words >= 1:
        earned.append(('🌱', 'Первое слово', 'Добавил первое слово'))
    if total_words >= 10:
        earned.append(('📚', '10 слов', 'Словарь растёт!'))
    if total_words >= 50:
        earned.append(('🏆', '50 слов', 'Серьёзный словарный запас'))
    if total_quizzes >= 1:
        earned.append(('⚡', 'Первый тест', 'Прошёл первый тест'))
    if total_quizzes >= 10:
        earned.append(('🔥', '10 тестов', 'Постоянный практик'))
    if accuracy >= 80:
        earned.append(('🎯', 'Меткий', 'Точность выше 80%'))
    if accuracy == 100 and total_quizzes > 0:
        earned.append(('💎', 'Перфекционист', 'Идеальная точность'))
    return earned


# ── External API proxies ──────────────────────────────────────────────────────

def api_suggest_translation(request):
    """Proxy to MyMemory API: suggest Russian translation for a word."""
    word = request.GET.get('word', '').strip()
    lang_pair = request.GET.get('langpair', 'en|ru')

    if not word:
        return JsonResponse({'error': 'Слово не указано'}, status=400)

    url = (
        'https://api.mymemory.translated.net/get?'
        + urllib.parse.urlencode({'q': word, 'langpair': lang_pair})
    )
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=API_TIMEOUT) as response:
            data = json.loads(response.read().decode())
        translated = data.get('responseData', {}).get('translatedText', '')
        if not translated or translated.upper() == word.upper():
            return JsonResponse({'translation': ''})
        return JsonResponse({'translation': translated.lower()})
    except (urllib.error.URLError, json.JSONDecodeError, KeyError):
        return JsonResponse({'error': 'Сервис перевода недоступен'}, status=503)


def api_suggest_example(request):
    """Proxy to Free Dictionary API: fetch an example sentence for an English word."""
    word = request.GET.get('word', '').strip().lower()

    if not word:
        return JsonResponse({'error': 'Слово не указано'}, status=400)

    url = f'https://api.dictionaryapi.dev/api/v2/entries/en/{urllib.parse.quote(word)}'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=API_TIMEOUT) as response:
            data = json.loads(response.read().decode())

        example = ''
        for entry in data:
            for meaning in entry.get('meanings', []):
                for definition in meaning.get('definitions', []):
                    if definition.get('example'):
                        example = definition['example']
                        break
                if example:
                    break
            if example:
                break

        return JsonResponse({'example': example})
    except urllib.error.HTTPError:
        return JsonResponse({'example': ''})
    except (urllib.error.URLError, json.JSONDecodeError, KeyError):
        return JsonResponse({'error': 'Dictionary API недоступен'}, status=503)


# ── Language views ────────────────────────────────────────────────────────────

@login_required
def language_list(request):
    """Render the list of all languages with inline create form."""
    if request.method == 'POST':
        form = LanguageForm(request.POST)
        if form.is_valid():
            lang = form.save()
            messages.success(request, f"✅ Язык «{lang.name}» добавлен.")
            return redirect('language_list')
    else:
        form = LanguageForm()

    languages = Language.objects.all()
    context = {'languages': languages, 'form': form}
    return render(request, 'trainer/language_list.html', context)


@login_required
def language_delete(request, pk):
    """Delete a language after confirmation."""
    language = get_object_or_404(Language, pk=pk)

    if request.method == 'POST':
        name = language.name
        language.delete()
        messages.warning(request, f"🗑️ Язык «{name}» удалён.")
        return redirect('language_list')

    return render(request, 'trainer/language_confirm_delete.html', {'language': language})


# ── Collection views ──────────────────────────────────────────────────────────

@login_required
def collection_list(request):
    """Render the list of collections owned by current user."""
    language_filter = request.GET.get('language', '')
    queryset = Collection.objects.filter(owner=request.user).select_related('language')

    if language_filter:
        queryset = queryset.filter(language__pk=language_filter)

    languages = Language.objects.all()
    context = {
        'collections': queryset,
        'languages': languages,
        'language_filter': language_filter,
    }
    return render(request, 'trainer/collection_list.html', context)


@login_required
def collection_detail(request, pk):
    """Show a collection and its words."""
    collection = get_object_or_404(Collection, pk=pk, owner=request.user)
    words = collection.words.order_by('-created_at')
    context = {'collection': collection, 'words': words}
    return render(request, 'trainer/collection_detail.html', context)


@login_required
def collection_create(request):
    """Handle collection creation."""
    if not Language.objects.exists():
        messages.warning(request, "⚠️ Сначала добавьте хотя бы один язык.")
        return redirect('language_list')

    if request.method == 'POST':
        form = CollectionForm(request.POST)
        if form.is_valid():
            collection = form.save(commit=False)
            collection.owner = request.user
            collection.save()
            messages.success(request, f"✅ Подборка «{collection.name}» создана.")
            return redirect('collection_detail', pk=collection.pk)
    else:
        form = CollectionForm()

    context = {
        'form': form,
        'title': 'Новая подборка',
        'submit_label': 'Создать',
    }
    return render(request, 'trainer/collection_form.html', context)


@login_required
def collection_edit(request, pk):
    """Handle collection editing."""
    collection = get_object_or_404(Collection, pk=pk, owner=request.user)

    if request.method == 'POST':
        form = CollectionForm(request.POST, instance=collection)
        if form.is_valid():
            form.save()
            messages.success(request, f"✏️ Подборка «{collection.name}» обновлена.")
            return redirect('collection_detail', pk=pk)
    else:
        form = CollectionForm(instance=collection)

    context = {
        'form': form,
        'collection': collection,
        'title': f'Редактировать: {collection.name}',
        'submit_label': 'Сохранить',
    }
    return render(request, 'trainer/collection_form.html', context)


@login_required
def collection_delete(request, pk):
    """Delete a collection after confirmation."""
    collection = get_object_or_404(Collection, pk=pk, owner=request.user)

    if request.method == 'POST':
        name = collection.name
        collection.delete()
        messages.warning(request, f"🗑️ Подборка «{name}» удалена.")
        return redirect('collection_list')

    return render(request, 'trainer/collection_confirm_delete.html', {'collection': collection})


# ── Word views ────────────────────────────────────────────────────────────────

@login_required
def word_list(request):
    """Render the word list filtered by current user."""
    queryset = Word.objects.filter(
        collection__owner=request.user
    ).select_related('collection__language')

    search = request.GET.get('search', '').strip()
    sort = request.GET.get('sort', '-created_at')
    collection_filter = request.GET.get('collection', '')

    if search:
        queryset = queryset.filter(
            Q(original__icontains=search) | Q(translation__icontains=search)
        )

    if collection_filter:
        queryset = queryset.filter(collection__pk=collection_filter)

    sort_options = {
        '-created_at': 'Сначала новые',
        'created_at': 'Сначала старые',
        'original': 'А–Я (оригинал)',
        'translation': 'А–Я (перевод)',
        '-times_shown': 'Больше тренировок',
    }
    if sort in sort_options:
        queryset = queryset.order_by(sort)

    collections = Collection.objects.filter(owner=request.user).select_related('language')
    context = {
        'words': queryset,
        'search': search,
        'sort': sort,
        'sort_options': sort_options,
        'collections': collections,
        'collection_filter': collection_filter,
        'total_count': queryset.count(),
    }
    return render(request, 'trainer/word_list.html', context)


@login_required
def word_detail(request, pk):
    """Render the detail page for a single word."""
    word = get_object_or_404(
        Word, pk=pk, collection__owner=request.user
    )
    return render(request, 'trainer/word_detail.html', {'word': word})


@login_required
def word_create(request):
    """Handle word creation."""
    if request.method == 'POST':
        form = WordForm(request.POST, user=request.user)
        if form.is_valid():
            word = form.save()
            messages.success(request, f"✅ Слово «{word.original}» добавлено.")
            if word.collection:
                return redirect('collection_detail', pk=word.collection.pk)
            return redirect('word_list')
    else:
        collection_pk = request.GET.get('collection')
        initial = {}
        if collection_pk:
            initial['collection'] = collection_pk
        form = WordForm(initial=initial, user=request.user)

    context = {
        'form': form,
        'title': 'Новое слово',
        'submit_label': 'Добавить',
    }
    return render(request, 'trainer/word_form.html', context)


@login_required
def word_edit(request, pk):
    """Handle word editing."""
    word = get_object_or_404(Word, pk=pk, collection__owner=request.user)

    if request.method == 'POST':
        form = WordForm(request.POST, instance=word, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f"✏️ Слово «{word.original}» обновлено.")
            return redirect('word_detail', pk=pk)
    else:
        form = WordForm(instance=word, user=request.user)

    context = {
        'form': form,
        'word': word,
        'title': f'Редактировать: {word.original}',
        'submit_label': 'Сохранить',
    }
    return render(request, 'trainer/word_form.html', context)


@login_required
def word_delete(request, pk):
    """Handle word deletion with confirmation."""
    word = get_object_or_404(Word, pk=pk, collection__owner=request.user)

    if request.method == 'POST':
        original = word.original
        collection = word.collection
        word.delete()
        messages.warning(request, f"🗑️ Слово «{original}» удалено.")
        if collection:
            return redirect('collection_detail', pk=collection.pk)
        return redirect('word_list')

    return render(request, 'trainer/word_confirm_delete.html', {'word': word})


# ── Quiz views ────────────────────────────────────────────────────────────────

@login_required
def quiz_start(request):
    """Render quiz settings page and initialise a quiz session."""
    if request.method == 'POST':
        form = QuizSettingsForm(request.POST, user=request.user)
        if form.is_valid():
            count = int(form.cleaned_data['count'])
            direction = form.cleaned_data['direction']
            collection = form.cleaned_data.get('collection')

            queryset = Word.objects.filter(collection__owner=request.user)
            if collection:
                queryset = queryset.filter(collection=collection)

            word_ids = list(queryset.values_list('id', flat=True))
            random.shuffle(word_ids)
            if count > 0:
                word_ids = word_ids[:count]

            if not word_ids:
                messages.warning(request, "⚠️ Нет слов для выбранных настроек.")
                return redirect('quiz_start')

            request.session['quiz_words'] = word_ids
            request.session['quiz_index'] = 0
            request.session['quiz_results'] = []
            request.session['quiz_direction'] = direction
            request.session['quiz_collection'] = collection.pk if collection else None

            return redirect('quiz_question')
    else:
        initial = {}
        preselect = request.GET.get('collection')
        if preselect:
            initial['collection'] = preselect
        form = QuizSettingsForm(initial=initial, user=request.user)

    word_count = Word.objects.filter(collection__owner=request.user).count()
    context = {
        'form': form,
        'word_count': word_count,
        'can_start': word_count >= MIN_WORDS_FOR_QUIZ,
    }
    return render(request, 'trainer/quiz_start.html', context)


@login_required
def quiz_question(request):
    """Show the current quiz question or redirect when quiz is complete."""
    word_ids = request.session.get('quiz_words', [])
    cur = request.session.get('quiz_index', 0)
    direction = request.session.get('quiz_direction', 'orig_trans')

    if not word_ids or cur >= len(word_ids):
        return redirect('quiz_results')

    word = get_object_or_404(Word, pk=word_ids[cur])

    if request.method == 'POST':
        form = QuizAnswerForm(request.POST)
        if form.is_valid():
            user_answer = form.cleaned_data['answer']
            correct = word.translation if direction == 'orig_trans' else word.original
            is_correct = user_answer.strip().lower() == correct.strip().lower()

            word.times_shown += 1
            if is_correct:
                word.times_correct += 1
            word.save(update_fields=['times_shown', 'times_correct'])

            results = request.session.get('quiz_results', [])
            results.append({
                'original': word.original,
                'translation': word.translation,
                'user_answer': user_answer,
                'correct_answer': correct,
                'is_correct': is_correct,
            })
            request.session['quiz_results'] = results
            request.session['quiz_index'] = cur + 1
            request.session.modified = True
            return redirect('quiz_question')
    else:
        form = QuizAnswerForm()

    question_text = word.original if direction == 'orig_trans' else word.translation
    total = len(word_ids)
    progress = round(cur / total * 100) if total > 0 else 0

    context = {
        'form': form,
        'question': question_text,
        'direction': direction,
        'current': cur + 1,
        'total': total,
        'progress': progress,
        'language': word.collection.language.name if word.collection else '',
    }
    return render(request, 'trainer/quiz_question.html', context)


@login_required
def quiz_results(request):
    """Show quiz results, save to DB and clear the quiz session."""
    results = request.session.get('quiz_results', [])

    if not results:
        return redirect('quiz_start')

    correct_count = sum(1 for entry in results if entry['is_correct'])
    total = len(results)
    score = round(correct_count / total * 100) if total > 0 else 0
    direction = request.session.get('quiz_direction', 'orig_trans')
    collection_pk = request.session.get('quiz_collection')

    collection = None
    if collection_pk:
        collection = Collection.objects.filter(pk=collection_pk).first()

    QuizResult.objects.create(
        owner=request.user,
        score=correct_count,
        total=total,
        direction=direction,
        collection=collection,
    )

    if score == 100:
        grade = ('🏆', 'Отлично!', 'success')
    elif score >= 80:
        grade = ('🎉', 'Хорошо!', 'success')
    elif score >= 60:
        grade = ('👍', 'Неплохо!', 'warning')
    else:
        grade = ('📚', 'Нужно практиковаться!', 'danger')

    for key in ['quiz_words', 'quiz_index', 'quiz_results', 'quiz_direction', 'quiz_collection']:
        request.session.pop(key, None)

    context = {
        'results': results,
        'correct_count': correct_count,
        'total': total,
        'score': score,
        'grade_icon': grade[0],
        'grade_text': grade[1],
        'grade_color': grade[2],
    }
    return render(request, 'trainer/quiz_results.html', context)
