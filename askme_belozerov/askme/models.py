from django.db import models
from django.contrib.auth.models import User as Users
from django.db.models import Count


class QuestionManager(models.Manager):
    def getTag(self, tag_name):
        tag = Tag.objects.get(name=tag_name)
        return self.filter(tag=tag).order_by('-id')

    def get_id(self, id):
        question = Question.objects.annotate(num_answers=Count('answers')).prefetch_related('author', 'tag').get(id=id)
        return question

    def new_questions(self):
        questions = Question.objects.annotate(num_answers=Count('answers')).prefetch_related('author', 'tag').order_by(
            '-id')
        return questions

    def count_questions(self):
        return self.count()


class AnswerManager(models.Manager):
    def mostPopular(self, question):
        return self.all().filter(question=question).order_by('-is_correct', '-score')


class TagManager:
    @staticmethod
    def mostPopular():
        return Tag.objects.annotate(num_questions=Count('question')).order_by('-num_questions')


class UserManager:
    @staticmethod
    def mostPopular():
        return User.objects.all().order_by('-score')


class User(models.Model):
    profile = models.OneToOneField(Users, on_delete=models.PROTECT)
    avatar = models.ImageField(null=True)
    nickname = models.CharField(max_length=40, unique=False)
    score = models.IntegerField(default=0)

    def __str__(self):
        return f'User "{self.nickname}"'

    objects = UserManager()


class Question(models.Model):
    text = models.TextField(default='question text')
    title = models.CharField(max_length=255, unique=False)
    author = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, related_name='questions')
    tag = models.ManyToManyField('Tag')
    score = models.IntegerField(default=0)

    def __str__(self):
        return f'Question "{self.title}"'

    objects = QuestionManager()


class Ratings(models.Model):
    title = models.TextField(default='title text')
    user = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, related_name='ratings')
    question = models.ForeignKey('Question', on_delete=models.CASCADE, null=True, related_name='question_ratings')
    answer = models.ForeignKey('Answer', on_delete=models.CASCADE, null=True, related_name='answer_ratings')
    positive = models.BooleanField(default=True)

    def __str__(self):
        return f'Ratings "{self.title}"'


class Tag(models.Model):
    name = models.CharField(max_length=40, unique=False)

    def __str__(self):
        return f'Tag "{self.name}"'

    objects = TagManager()


class Answer(models.Model):
    text = models.TextField(default='answer text')
    question = models.ForeignKey('Question', on_delete=models.CASCADE, related_name='answers')
    author = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, related_name='answers')
    score = models.IntegerField(default=0)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f'Answer to "{self.text}"'

    objects = AnswerManager()