from django.core.paginator import Paginator
from django.shortcuts import render
from . import models
from .models import Question
from django.http import HttpResponseNotFound, Http404


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


def question(request, question_id):
    try:
        question_id = int(question_id)
        our_question = models.Question.objects.filter(id=question_id)
        if not our_question:
            raise Http404
        questions_page = Question.objects.new_questions()
        questions = paginate(questions_page, request)
        tags_page = models.TagManager.mostPopular()
        members_page = models.TagManager.mostPopular()
        question_page = Question.objects.get_id(question_id)
        context = {'questions': questions,
                   'question':question_page,
                   'tags': tags_page,
                   'best_members': members_page}
        return render(request, "question.html", context)
    except ValueError:
        return HttpResponseNotFound('Invalid question ID')


def settings(request):
    tags_page = models.TagManager.mostPopular()
    members_page = models.TagManager.mostPopular()
    context = {'tags': tags_page,
               'best_members': members_page}
    return render(request, 'settings.html', context)


def registration(request):
    tags_page = models.TagManager.mostPopular()
    members_page = models.TagManager.mostPopular()
    context = {'tags': tags_page,
               'best_members': members_page}
    return render(request, 'registration.html', context)


def login(request):
    tags_page = models.TagManager.mostPopular()
    members_page = models.TagManager.mostPopular()
    context = {'tags': tags_page,
               'best_members': members_page}
    return render(request, 'login.html', context)


def ask(request):
    tags_page = models.TagManager.mostPopular()
    members_page = models.TagManager.mostPopular()
    context = {'tags': tags_page,
               'best_members': members_page}
    return render(request, 'ask.html', context)


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
