from django.http import HttpResponse, HttpResponseNotFound
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from . import models
from .models import TAGS


def index(request):
    questions = models.QUESTIONS
    paginator = Paginator(questions, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    tags = TAGS
    context = {'questions': page_obj, 'tags': tags}
    return render(request, 'index.html', context)


def hot(request):
    questions = models.QUESTIONS
    paginator = Paginator(questions, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'questions': page_obj}
    return render(request, 'hot.html', context)


def question(request, question_id):
    try:
        question_id = int(question_id)
        if question_id >= len(models.QUESTIONS):
            return HttpResponseNotFound('Invalid question ID')
        context = {'question': models.QUESTIONS[question_id],
                   'answers': models.ANSWERS,
                   'tags': models.TAGS}
        return render(request, "question.html", context)
    except ValueError:
        return HttpResponseNotFound('Invalid question ID')



def settings(request):
    return render(request, 'settings.html')


def registration(request):
    return render(request, 'registration.html')


def login(request):
    return render(request, 'login.html')


def ask(request):
    return render(request, 'ask.html')


def tag(request, tag_name):
    tag = [tag_name] * 3;
    context = {
        'tags': tag,
    }
    return render(request, 'tag.html', context)

def paginate(objects_list, request, per_page=5):
    paginator = Paginator(objects_list, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj, paginator
