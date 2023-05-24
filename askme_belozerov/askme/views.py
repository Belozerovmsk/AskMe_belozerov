from django.core.paginator import Paginator
from django.shortcuts import render
from . import models
from .models import Question, Answer, User, Tag
from django.http import HttpResponseNotFound, Http404
from django.urls import reverse
from . import forms
from django.contrib import auth
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout

from django.urls import reverse

from django.contrib import auth
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


from .models import User as UserProfile
from django.db.models import Count



def index(request):
    questions_page = Question.objects.new_questions()
    questions = paginate(questions_page, request)
    tags_page = models.TagManager.mostPopular()
    members_page = models.TagManager.mostPopular()
    context = {'questions': questions,
               'tags': tags_page,
               'best_members': members_page}
    return render(request, "index.html", context)


def hot(request):
    questions_page = Question.objects.new_questions()
    questions = paginate(questions_page, request)
    tags_page = models.TagManager.mostPopular()
    members_page = models.TagManager.mostPopular()
    context = {'questions': questions,
               'tags': tags_page,
               'best_members': members_page}
    return render(request, 'hot.html', context)



def question(request, question_id, page_num=1):
    question_page = Question.objects.get_id(question_id)

    if request.method =='GET':
        answer_form = forms.AnswerForm()
    elif request.method == 'POST':
        answer_form = forms.AnswerForm(request.POST)
        if answer_form.is_valid():
            answer = answer_form.save(request.user.user, question_page)
            answers = paginate(Answer.objects.most_popular(question_page), request)
            page_num = answers.paginator.num_pages
            return redirect(reverse('question_page', args=(question_id, page_num)) + f'?page={page_num}#{answer.id}')
        else:
            answer_form.add_error("Invalid parameters")

    tags_page = models.TagManager.mostPopular()
    answers = paginate(Answer.objects.mostPopular(question_page), request)
    best_members = models.TagManager.mostPopular()
    questions_page = Question.objects.new_questions()
    questions = paginate(questions_page, request)
    context = {'question': question_page,
               'questions': questions,
               'tags': tags_page,
               'answers': answers,
               'best_members': best_members,
               'form': answer_form,
               'page_num': page_num}
    return render(request, "question.html", context)


@login_required
def settings(request):
    tags_page = models.TagManager.mostPopular()
    members_page = models.TagManager.mostPopular()
    context = {'tags': tags_page,
               'best_members': members_page}
    return render(request, 'settings.html', context)

def registration(request):
    if request.method == 'GET':
        user_form = forms.RegistrationForm()
    if request.method == 'POST':
        user_form = forms.RegistrationForm(request.POST)
        if user_form.is_valid():
            user = user_form.save()
            if user:
                return redirect('index')
            else:
                user_form.add_error(field=None, error="User saving error!")

    tags_page = models.TagManager.mostPopular()
    members_page = models.TagManager.mostPopular()

    context = {'tags': tags_page,
               'best_members': members_page,
               'form': user_form}
    return render(request, "registration.html", context)


def login(request):
    if request.method == 'GET':
        login_form = forms.LoginForm()
    elif request.method == 'POST':
        login_form = forms.LoginForm(request.POST)
        if login_form.is_valid():
            user = auth.authenticate(request=request, **login_form.cleaned_data)
            if user:
                auth.login(request, user)
                return redirect('index')
            login_form.add_error(None, "Username or password is incorrect")
    tags_page = models.TagManager.mostPopular()
    members_page = models.TagManager.mostPopular()
    context = {'tags': tags_page,
               'best_members': members_page,
                'form': login_form}
    return render(request, "login.html", context=context)


@login_required
def ask(request):
    if request.method == 'GET':
        question_form = forms.QuestionForm()
    if request.method == 'POST':
        question_form = forms.QuestionForm(request.POST)
        if question_form.is_valid():
            profile = request.user
            question = question_form.save(profile.user)
            return redirect('question', question.id)
    tags_page = models.TagManager.mostPopular()
    members_page = models.TagManager.mostPopular()
    context = {'tags': tags_page,
               'best_members': members_page,
               'form': question_form}
    return render(request, "ask.html", context)



def tag(request, tag_name):
    questions = Question.objects.filter(tag__name__in=[tag_name]).order_by('id')
    tags = models.TagManager.mostPopular()
    members = models.TagManager.mostPopular()
    if not questions:
        return HttpResponseNotFound('Invalid tag question')

    paginator = Paginator(questions, per_page=10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'questions': page_obj,
               'tags': tags,
               'best_members': members}
    return render(request, 'tag.html', context)


def paginate(objects_list, request, per_page=5):
    paginator = Paginator(objects_list, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


@login_required
def log_out(request):
    logout(request)
    return redirect(request.META.get('HTTP_REFERER'))
