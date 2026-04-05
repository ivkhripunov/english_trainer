"""URL configuration for the trainer application."""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),

    # Auth
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Profile
    path('profile/', views.profile, name='profile'),

    # External API proxies
    path('api/translate/', views.api_suggest_translation, name='api_translate'),
    path('api/example/', views.api_suggest_example, name='api_example'),

    # Languages
    path('languages/', views.language_list, name='language_list'),
    path('languages/<int:pk>/delete/', views.language_delete, name='language_delete'),

    # Collections
    path('collections/', views.collection_list, name='collection_list'),
    path('collections/add/', views.collection_create, name='collection_create'),
    path('collections/<int:pk>/', views.collection_detail, name='collection_detail'),
    path('collections/<int:pk>/edit/', views.collection_edit, name='collection_edit'),
    path('collections/<int:pk>/delete/', views.collection_delete, name='collection_delete'),

    # Words
    path('words/', views.word_list, name='word_list'),
    path('words/add/', views.word_create, name='word_create'),
    path('words/<int:pk>/', views.word_detail, name='word_detail'),
    path('words/<int:pk>/edit/', views.word_edit, name='word_edit'),
    path('words/<int:pk>/delete/', views.word_delete, name='word_delete'),

    # Quiz
    path('quiz/', views.quiz_start, name='quiz_start'),
    path('quiz/question/', views.quiz_question, name='quiz_question'),
    path('quiz/results/', views.quiz_results, name='quiz_results'),
]
