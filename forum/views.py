from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Question, Answer
from .forms import QuestionForm, AnswerForm

@login_required
def like_question(request, pk):
    question = get_object_or_404(Question, pk=pk)
    if request.user in question.likes.all():
        question.likes.remove(request.user)
    else:
        question.likes.add(request.user)
        question.dislikes.remove(request.user)
    return redirect('forum:question_detail', pk=pk)

@login_required
def dislike_question(request, pk):
    question = get_object_or_404(Question, pk=pk)
    if request.user in question.dislikes.all():
        question.dislikes.remove(request.user)
    else:
        question.dislikes.add(request.user)
        question.likes.remove(request.user)
    return redirect('forum:question_detail', pk=pk)

@login_required
def like_answer(request, pk):
    answer = get_object_or_404(Answer, pk=pk)
    if request.user in answer.likes.all():
        answer.likes.remove(request.user)
    else:
        answer.likes.add(request.user)
        answer.dislikes.remove(request.user)
    return redirect('forum:question_detail', pk=answer.question.pk)

@login_required
def dislike_answer(request, pk):
    answer = get_object_or_404(Answer, pk=pk)
    if request.user in answer.dislikes.all():
        answer.dislikes.remove(request.user)
    else:
        answer.dislikes.add(request.user)
        answer.likes.remove(request.user)
    return redirect('forum:question_detail', pk=answer.question.pk)

def question_list(request):
    questions = Question.objects.all().select_related('user').prefetch_related('answers')
    return render(request, 'forum/question_list.html', {'questions': questions})

def question_detail(request, pk):
    question = get_object_or_404(Question, pk=pk)
    answers = question.answers.all().select_related('user')
    
    if request.method == 'POST' and request.user.is_authenticated:
        form = AnswerForm(request.POST, request.FILES)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.user = request.user
            answer.question = question
            answer.save()
            return redirect('forum:question_detail', pk=pk)
    else:
        form = AnswerForm()
        
    return render(request, 'forum/question_detail.html', {
        'question': question,
        'answers': answers,
        'form': form
    })

@login_required
def ask_question(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST, request.FILES)
        if form.is_valid():
            question = form.save(commit=False)
            question.user = request.user
            question.save()
            return redirect('forum:question_list')
    else:
        form = QuestionForm()
        
    return render(request, 'forum/ask_question.html', {'form': form})
