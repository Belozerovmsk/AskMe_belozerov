from django.db import models
from django.contrib.auth.models import User as Users
from django.db.models import Count
from django.contrib.auth.models import User


class QuestionManager(models.Manager):
    def getTag(self, tag_name):
        return self.annotate(num_questions=models.Count('questions')).order_by('-num_questions')[:4]

    def get_id(self, id):
        question = Question.objects.annotate(num_answers=Count('answer')).prefetch_related('user_profile', 'tags').get(id=id)
        return question

    def new_questions(self):
        return self.order_by('-id')

    def hot_questions(self):
        return self.annotate(num_likes=models.Count('likes')).order_by('-num_likes', 'id')

    def count_questions(self):
        return self.count()


class AnswerManager(models.Manager):
    def mostPopular(self, question):
        return self.all().filter(question=question).order_by('-is_correct', '-likes')


class TagManager:
    @staticmethod
    def mostPopular():
        return Tag.objects.annotate(num_questions=Count('questions')).order_by('-num_questions')


class UserManager(models.Manager):
    def mostPopular(self):
        return self.annotate(num_answers=models.Count('answer')).order_by('-num_answers')[:5]


class Profile(models.Model):
    profile = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/%Y/%m/%d/', default='upload/User.png')

    def __str__(self):
        return self.profile.username

    objects = UserManager()


class Tag(models.Model):
    name = models.CharField(max_length=25)

    def __str__(self):
        return self.name

    objects = TagManager()


class Question(models.Model):
    name = models.CharField(max_length=255, default='Simple Question')
    text = models.TextField()
    likes = models.ManyToManyField(Profile, through='LikedQuestions', related_name='liked_questions', blank=True)
    user_profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    tags = models.ManyToManyField(Tag, related_name='questions')
    def __str__(self):
        return self.name
    objects = QuestionManager()


class Answer(models.Model):
    text = models.TextField()
    likes = models.ManyToManyField(Profile, through='LikedAnswers', related_name='liked_answers', blank=True)
    is_correct = models.BooleanField(default=False)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user_profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f'{self.user_profile.profile.username} answer to question: "{self.question.name}"'

    objects = AnswerManager()


class LikedAnswers(models.Model):
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    user_profile = models.ForeignKey(Profile, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['answer', 'user_profile'], name='unique_answer_likes')
        ]

    def __str__(self):
        return f'{self.user_profile.profile.username} liked answer "{self.answer.pk}"'


class LikedQuestions(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user_profile = models.ForeignKey(Profile, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['question', 'user_profile'], name='unique_question_likes')
        ]

    def __str__(self):
        return f'{self.user_profile.profile.username} rate question "{self.question.name}"'