
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from faker import Faker
from askme import models
import uuid
import random


from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from faker import Faker
import random

class Command(BaseCommand):
    help = 'BD FILL'

    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int, help='bd filling coefficient')

    def handle(self, *args, **kwargs):
        ratio = kwargs['ratio']

        fake = Faker()

        users = [User(username=f'{fake.word()}{i}_{uuid.uuid4().hex[:8]}', password='password') for i in range(ratio)]
        User.objects.bulk_create(users)
        self.stdout.write("USERS FILLED\n")

        profiles = [models.User(profile=user, nickname=fake.user_name()) for user in users]
        models.User.objects.bulk_create(profiles)
        self.stdout.write("PROFILES FILLED\n")

        tags = [models.Tag(name=fake.word()) for i in range(ratio)]
        models.Tag.objects.bulk_create(tags)
        self.stdout.write("TAGS FILLED\n")

        questions = []
        for i in range(ratio):
            for j in range(10):
                question = models.Question(title=fake.sentence(), text=fake.text(), author=random.choice(profiles), score=i)
                questions.append(question)
        models.Question.objects.bulk_create(questions)

        for question in questions:
            question.tag.add(random.choice(tags))
        self.stdout.write("QUESTIONS FILLED\n")

        answers = []
        for i in range(ratio * 100):
            answer = models.Answer(text=fake.text(), question=random.choice(questions), author=random.choice(profiles), is_correct=random.choice([True, False]), score=i)
            answers.append(answer)
        models.Answer.objects.bulk_create(answers)
        self.stdout.write("ANSWERS FILLED\n")

        ratings = []
        for i in range(ratio * 200):
            rating = models.Ratings(title=fake.text(), user=random.choice(profiles), positive=random.choice([True, False]))
            if random.choice([True, False]):
                rating.question = random.choice(questions)
            else:
                rating.answer = random.choice(answers)
            ratings.append(rating)
        models.Ratings.objects.bulk_create(ratings)
        self.stdout.write("RATINGS FILLED\n")

        self.stdout.write("DONE")
