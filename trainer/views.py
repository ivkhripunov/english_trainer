"""Views for the English trainer application."""
import random
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q, Sum

from .models import Word, Collection, Language
from .forms import WordForm, QuizAnswerForm, QuizSettingsForm, CollectionForm, LanguageForm

MIN_WORDS_FOR_QUIZ = 1


# ── Home ──────────────────────────────────────────────────────────────────────

def index(request):
    """Render the home page with overall statistics."""
    total_words = Word.objects.count()
    total_collections = Collection.objects.count()
    total_languages = Language.objects.count()
    recent_collections = Collection.objects.select_related('language').order_by('-created_at')[:4]

    aggregates = Word.objects.aggregate(
        total_shown=Sum('times_shown'),
        total_correct=Sum('times_correct'),
    )
    total_shown = aggregates['total_shown'] or 0
    total_correct = aggregates['total_correct'] or 0
    overall_accuracy = (
        round(total_correct / total_shown * 100) if total_shown > 0 else 0
    )

    hardest_words = (
        Word.objects.filter(times_shown__gt=0)
        .select_related('collection__language')
        .order_by('times_correct', '-times_shown')[:3]
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


# ── Language views ────────────────────────────────────────────────────────────

def language_list(request):
    """Render the list of all languages with inline create form."""
    if request.method == 'POST':
        form = LanguageForm(request.POST)
        if form.is_valid():
            lang = form.save()
            messages.success(request, f"✅ Language «{lang.name}» added.")
            return redirect('language_list')
    else:
        form = LanguageForm()

    languages = Language.objects.all()
    context = {'languages': languages, 'form': form}
    return render(request, 'trainer/language_list.html', context)


def language_delete(request, pk):
    """Delete a language after confirmation."""
    language = get_object_or_404(Language, pk=pk)

    if request.method == 'POST':
        name = language.name
        language.delete()
        messages.warning(request, f"🗑️ Language «{name}» deleted.")
        return redirect('language_list')

    return render(request, 'trainer/language_confirm_delete.html', {'language': language})


# ── Collection views ──────────────────────────────────────────────────────────

def collection_list(request):
    """Render the list of all collections."""
    language_filter = request.GET.get('language', '')
    queryset = Collection.objects.select_related('language')

    if language_filter:
        queryset = queryset.filter(language__pk=language_filter)

    languages = Language.objects.all()
    context = {
        'collections': queryset,
        'languages': languages,
        'language_filter': language_filter,
    }
    return render(request, 'trainer/collection_list.html', context)


def collection_detail(request, pk):
    """Show a collection and its words."""
    collection = get_object_or_404(Collection, pk=pk)
    words = collection.words.order_by('-created_at')
    context = {'collection': collection, 'words': words}
    return render(request, 'trainer/collection_detail.html', context)


def collection_create(request):
    """Handle collection creation."""
    if not Language.objects.exists():
        messages.warning(
            request,
            "⚠️ Please add at least one language before creating a collection."
        )
        return redirect('language_list')

    if request.method == 'POST':
        form = CollectionForm(request.POST)
        if form.is_valid():
            collection = form.save()
            messages.success(request, f"✅ Collection «{collection.name}» created.")
            return redirect('collection_detail', pk=collection.pk)
    else:
        form = CollectionForm()

    context = {
        'form': form,
        'title': 'New Collection',
        'submit_label': 'Create Collection',
    }
    return render(request, 'trainer/collection_form.html', context)


def collection_edit(request, pk):
    """Handle collection editing."""
    collection = get_object_or_404(Collection, pk=pk)

    if request.method == 'POST':
        form = CollectionForm(request.POST, instance=collection)
        if form.is_valid():
            form.save()
            messages.success(request, f"✏️ Collection «{collection.name}» updated.")
            return redirect('collection_detail', pk=pk)
    else:
        form = CollectionForm(instance=collection)

    context = {
        'form': form,
        'collection': collection,
        'title': f'Edit: {collection.name}',
        'submit_label': 'Save Changes',
    }
    return render(request, 'trainer/collection_form.html', context)


def collection_delete(request, pk):
    """Delete a collection after confirmation."""
    collection = get_object_or_404(Collection, pk=pk)

    if request.method == 'POST':
        name = collection.name
        collection.delete()
        messages.warning(request, f"🗑️ Collection «{name}» deleted.")
        return redirect('collection_list')

    return render(request, 'trainer/collection_confirm_delete.html', {'collection': collection})


# ── Word views ────────────────────────────────────────────────────────────────

def word_list(request):
    """Render the word list with search, sort, and collection filter."""
    queryset = Word.objects.select_related('collection__language')

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
        '-created_at': 'Newest first',
        'created_at': 'Oldest first',
        'original': 'A–Z (original)',
        'translation': 'А–Я (translation)',
        '-times_shown': 'Most practiced',
    }
    if sort in sort_options:
        queryset = queryset.order_by(sort)

    collections = Collection.objects.select_related('language')
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


def word_detail(request, pk):
    """Render the detail page for a single word."""
    word = get_object_or_404(Word, pk=pk)
    return render(request, 'trainer/word_detail.html', {'word': word})


def word_create(request):
    """Handle word creation."""
    if request.method == 'POST':
        form = WordForm(request.POST)
        if form.is_valid():
            word = form.save()
            messages.success(request, f"✅ Word «{word.original}» added.")
            if word.collection:
                return redirect('collection_detail', pk=word.collection.pk)
            return redirect('word_list')
    else:
        collection_pk = request.GET.get('collection')
        initial = {}
        if collection_pk:
            initial['collection'] = collection_pk
        form = WordForm(initial=initial)

    context = {
        'form': form,
        'title': 'Add New Word',
        'submit_label': 'Add Word',
    }
    return render(request, 'trainer/word_form.html', context)


def word_edit(request, pk):
    """Handle word editing."""
    word = get_object_or_404(Word, pk=pk)

    if request.method == 'POST':
        form = WordForm(request.POST, instance=word)
        if form.is_valid():
            form.save()
            messages.success(request, f"✏️ Word «{word.original}» updated.")
            return redirect('word_detail', pk=pk)
    else:
        form = WordForm(instance=word)

    context = {
        'form': form,
        'word': word,
        'title': f'Edit: {word.original}',
        'submit_label': 'Save Changes',
    }
    return render(request, 'trainer/word_form.html', context)


def word_delete(request, pk):
    """Handle word deletion with confirmation."""
    word = get_object_or_404(Word, pk=pk)

    if request.method == 'POST':
        original = word.original
        collection = word.collection
        word.delete()
        messages.warning(request, f"🗑️ Word «{original}» deleted.")
        if collection:
            return redirect('collection_detail', pk=collection.pk)
        return redirect('word_list')

    return render(request, 'trainer/word_confirm_delete.html', {'word': word})


# ── Quiz views ────────────────────────────────────────────────────────────────

def quiz_start(request):
    """Render quiz settings page and initialise a quiz session."""
    if request.method == 'POST':
        form = QuizSettingsForm(request.POST)
        if form.is_valid():
            count = int(form.cleaned_data['count'])
            direction = form.cleaned_data['direction']
            collection = form.cleaned_data.get('collection')

            queryset = Word.objects.all()
            if collection:
                queryset = queryset.filter(collection=collection)

            word_ids = list(queryset.values_list('id', flat=True))
            random.shuffle(word_ids)
            if count > 0:
                word_ids = word_ids[:count]

            if not word_ids:
                messages.warning(request, "⚠️ No words found for the selected settings.")
                return redirect('quiz_start')

            request.session['quiz_words'] = word_ids
            request.session['quiz_index'] = 0
            request.session['quiz_results'] = []
            request.session['quiz_direction'] = direction
            request.session['quiz_collection'] = collection.pk if collection else None

            return redirect('quiz_question')
    else:
        form = QuizSettingsForm()

    word_count = Word.objects.count()
    context = {
        'form': form,
        'word_count': word_count,
        'can_start': word_count >= MIN_WORDS_FOR_QUIZ,
    }
    return render(request, 'trainer/quiz_start.html', context)


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


def quiz_results(request):
    """Show quiz results and clear the quiz session."""
    results = request.session.get('quiz_results', [])

    if not results:
        return redirect('quiz_start')

    correct_count = sum(1 for entry in results if entry['is_correct'])
    total = len(results)
    score = round(correct_count / total * 100) if total > 0 else 0

    if score == 100:
        grade = ('🏆', 'Perfect!', 'success')
    elif score >= 80:
        grade = ('🎉', 'Great job!', 'success')
    elif score >= 60:
        grade = ('👍', 'Good effort!', 'warning')
    else:
        grade = ('📚', 'Keep practising!', 'danger')

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
