from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Question, Answer
from .forms import QuestionForm, AnswerForm

def question_list(request):
    questions = Question.objects.all().select_related('user').prefetch_related('answers')
    return render(request, 'forum/question_list.html', {'questions': questions})

def question_detail(request, pk):
    question = get_object_or_404(Question, pk=pk)
    answers = question.answers.all().select_related('user')
    
    if request.method == 'POST' and request.user.is_authenticated:
        form = AnswerForm(request.POST)
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
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.user = request.user
            question.save()
            return redirect('forum:question_list')
    else:
        form = QuestionForm()
        
    return render(request, 'forum/ask_question.html', {'form': form})
