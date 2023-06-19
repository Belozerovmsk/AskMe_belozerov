from . import models
from .models import Question, Answer
from . import forms
from django.urls import reverse
from django.contrib import auth
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponseNotFound
from django.core.paginator import Paginator
from django.forms import model_to_dict
from django.contrib.auth import authenticate
from django.views.decorators.http import require_http_methods


def index(request):
    questions_page = Question.objects.new_questions()
    questions = paginate(questions_page, request)
    tags_page = models.TagManager.mostPopular()
    members_page = models.Profile.objects.mostPopular()
    context = {'questions': questions,
               'tags': tags_page,
               'best_members': members_page}
    return render(request, "index.html", context)


def hot(request):
    questions_page = Question.objects.hot_questions()
    questions = paginate(questions_page, request)
    tags_page = models.TagManager.mostPopular()
    members_page = models.Profile.objects.mostPopular()
    context = {'questions': questions,
               'tags': tags_page,
               'best_members': members_page}
    return render(request, 'hot.html', context)


@login_required(login_url='/login/')
def question(request, question_id, page_num=1):
    question_page = Question.objects.get_id(question_id)
    if request.method == 'GET':
        answer_form = forms.AnswerForm()
    else:
        answer_form = forms.AnswerForm(request.POST)
        if answer_form.is_valid():
            answer = answer_form.save(request, question_id)
            answers = paginate(Answer.objects.mostPopular(question_page), request)
            page_num = answers.paginator.num_pages
            return redirect(reverse('question_page', args=(question_id, page_num)) + f'?page={page_num}#{answer.id}')
        else:
            answer_form.add_error("Invalid arguments")
    tags_page = models.TagManager.mostPopular()
    answers = paginate(Answer.objects.mostPopular(question_page), request)
    best_members = models.Profile.objects.mostPopular()
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
@require_http_methods(['GET', 'POST'])
def settings(request):
    account = None
    setting_form = forms.SettingForm()

    if request.user.is_authenticated:
        user = models.User.objects.get(username=request.user)
        account = models.Profile.objects.get(profile=user)

    if request.method == 'POST':
        setting_form = forms.SettingForm(request.POST, files=request.FILES)
        if setting_form.is_valid():
            password = setting_form.cleaned_data.get('password')
            if account and not account.profile.check_password(password):
                setting_form.add_error(None, 'Current password is incorrect')
            else:
                setting_form.save(request)
                return redirect(reverse('settings'))

    tags_page = models.TagManager.mostPopular()
    members_page = models.Profile.objects.mostPopular()
    context = {
        'tags': tags_page,
        'best_members': members_page,
        'form': setting_form
    }
    return render(request, "settings.html", context=context)


def registration(request):
    if request.method == 'GET':
        user_form = forms.RegistrationForm()
    if request.method == 'POST':
        user_form = forms.RegistrationForm(request.POST)
        if user_form.is_valid():
            user_form.save(request)
            username = user_form.cleaned_data.get('username')
            password = user_form.cleaned_data.get('password')
            user_auth = auth.authenticate(username=username, password=password)
            auth.login(request, user_auth)
            return redirect('index')
    tags_page = models.TagManager.mostPopular()
    members_page = models.Profile.objects.mostPopular()

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
    members_page = models.Profile.objects.mostPopular()
    context = {'tags': tags_page,
               'best_members': members_page,
                'form': login_form}
    return render(request, "login.html", context=context)


@login_required(login_url='/login/')
def ask(request):
    if request.method == 'GET':
        question_form = forms.QuestionForm()
    if request.method == 'POST':
        question_form = forms.QuestionForm(request.POST)
        if question_form.is_valid():
            question = question_form.save(request.user.profile)
            return redirect('question', question.id)
    tags_page = models.TagManager.mostPopular()
    members_page = models.Profile.objects.mostPopular()
    context = {'tags': tags_page,
               'best_members': members_page,
               'form': question_form}
    return render(request, "ask.html", context)


def tag(request, tag_name):
    questions = Question.objects.filter(tags__name__in=[tag_name]).order_by('id')
    tags = models.TagManager.mostPopular()
    if not questions:
        return HttpResponseNotFound('Invalid tag question')

    paginator = Paginator(questions, per_page=10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    members_page = models.Profile.objects.mostPopular()

    context = {'questions': page_obj,
               'tags': tags,
               'best_members': members_page,
               'tag_name': tag_name}
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
