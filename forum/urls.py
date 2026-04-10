from django.urls import path
from . import views

app_name = 'forum'

urlpatterns = [
    path('', views.question_list, name='question_list'),
    path('question/<int:pk>/', views.question_detail, name='question_detail'),
    path('poser-une-question/', views.ask_question, name='ask_question'),
    path('question/<int:pk>/like/', views.like_question, name='like_question'),
    path('question/<int:pk>/dislike/', views.dislike_question, name='dislike_question'),
    path('answer/<int:pk>/like/', views.like_answer, name='like_answer'),
    path('answer/<int:pk>/dislike/', views.dislike_answer, name='dislike_answer'),
]
