"""Views for the English trainer application."""
import random
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q, Sum

from .models import Word
from .forms import WordForm, QuizAnswerForm, QuizSettingsForm

MIN_WORDS_FOR_QUIZ = 1


def index(request):
    """Render the home page with overall statistics."""
    total_words = Word.objects.count()
    recent_words = Word.objects.order_by('-created_at')[:5]

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
        .order_by('times_correct', '-times_shown')[:3]
    )

    context = {
        'total_words': total_words,
        'recent_words': recent_words,
        'overall_accuracy': overall_accuracy,
        'total_shown': total_shown,
        'hardest_words': hardest_words,
    }
    return render(request, 'trainer/index.html', context)


def word_list(request):
    """Render the word list with search and sort functionality."""
    queryset = Word.objects.all()

    search = request.GET.get('search', '').strip()
    sort = request.GET.get('sort', '-created_at')

    if search:
        queryset = queryset.filter(
            Q(english__icontains=search) | Q(russian__icontains=search)
        )

    sort_options = {
        '-created_at': 'Newest first',
        'created_at': 'Oldest first',
        'english': 'A–Z (English)',
        'russian': 'А–Я (Russian)',
        '-times_shown': 'Most practiced',
    }
    if sort in sort_options:
        queryset = queryset.order_by(sort)

    context = {
        'words': queryset,
        'search': search,
        'sort': sort,
        'sort_options': sort_options,
        'total_count': queryset.count(),
    }
    return render(request, 'trainer/word_list.html', context)


def word_detail(request, pk):
    """Render the detail page for a single word."""
    word = get_object_or_404(Word, pk=pk)
    return render(request, 'trainer/word_detail.html', {'word': word})


def word_create(request):
    """Handle word creation form."""
    if request.method == 'POST':
        form = WordForm(request.POST)
        if form.is_valid():
            word = form.save()
            messages.success(
                request,
                f"✅ Word «{word.english}» has been added successfully!"
            )
            return redirect('word_list')
    else:
        form = WordForm()

    context = {
        'form': form,
        'title': 'Add New Word',
        'submit_label': 'Add Word',
    }
    return render(request, 'trainer/word_form.html', context)


def word_edit(request, pk):
    """Handle word editing form."""
    word = get_object_or_404(Word, pk=pk)

    if request.method == 'POST':
        form = WordForm(request.POST, instance=word)
        if form.is_valid():
            form.save()
            messages.success(request, f"✏️ Word «{word.english}» updated.")
            return redirect('word_detail', pk=pk)
    else:
        form = WordForm(instance=word)

    context = {
        'form': form,
        'word': word,
        'title': f'Edit: {word.english}',
        'submit_label': 'Save Changes',
    }
    return render(request, 'trainer/word_form.html', context)


def word_delete(request, pk):
    """Handle word deletion with confirmation."""
    word = get_object_or_404(Word, pk=pk)

    if request.method == 'POST':
        english = word.english
        word.delete()
        messages.warning(request, f"🗑️ Word «{english}» has been deleted.")
        return redirect('word_list')

    return render(request, 'trainer/word_confirm_delete.html', {'word': word})


# ── Quiz views ────────────────────────────────────────────────────────────────

def quiz_start(request):
    """Render quiz settings page and initialise a quiz session."""
    word_count = Word.objects.count()

    if request.method == 'POST':
        form = QuizSettingsForm(request.POST)
        if form.is_valid():
            count = int(form.cleaned_data['count'])
            direction = form.cleaned_data['direction']

            word_ids = list(Word.objects.values_list('id', flat=True))
            random.shuffle(word_ids)
            if count > 0:
                word_ids = word_ids[:count]

            request.session['quiz_words'] = word_ids
            request.session['quiz_index'] = 0
            request.session['quiz_results'] = []
            request.session['quiz_direction'] = direction

            return redirect('quiz_question')
    else:
        form = QuizSettingsForm()

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
    direction = request.session.get('quiz_direction', 'en_ru')

    if not word_ids or cur >= len(word_ids):
        return redirect('quiz_results')

    word = get_object_or_404(Word, pk=word_ids[cur])

    if request.method == 'POST':
        form = QuizAnswerForm(request.POST)
        if form.is_valid():
            user_answer = form.cleaned_data['answer']
            correct = word.russian if direction == 'en_ru' else word.english
            is_correct = user_answer.strip().lower() == correct.strip().lower()

            word.times_shown += 1
            if is_correct:
                word.times_correct += 1
            word.save(update_fields=['times_shown', 'times_correct'])

            results = request.session.get('quiz_results', [])
            results.append({
                'english': word.english,
                'russian': word.russian,
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

    question_text = word.english if direction == 'en_ru' else word.russian
    total = len(word_ids)
    progress = round(cur / total * 100) if total > 0 else 0

    context = {
        'form': form,
        'question': question_text,
        'direction': direction,
        'current': cur + 1,
        'total': total,
        'progress': progress,
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

    for key in ['quiz_words', 'quiz_index', 'quiz_results', 'quiz_direction']:
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
