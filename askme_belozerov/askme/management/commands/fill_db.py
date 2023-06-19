from askme import models
import uuid
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from faker import Faker
import random

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int, help='bd filling coefficient')

    def handle(self, *args, **kwargs):
        ratio = kwargs['ratio']

        fake = Faker()

        profiles = []
        for i in range(1, ratio + 1):
            user = User.objects.create(username=f'user{i}')
            user.set_password(f'django{i}')
            profile = models.Profile(profile=user)
            profiles.append(profile)
        models.Profile.objects.bulk_create(profiles)
        self.stdout.write("PROFILES FILLED\n")

        tags = [models.Tag(name=fake.word()) for i in range(ratio)]
        models.Tag.objects.bulk_create(tags)
        self.stdout.write("TAGS FILLED\n")

        questions = []
        for i in range(ratio * 10):
            question = models.Question(name=fake.sentence(), text=fake.text(), user_profile=random.choice(profiles))
            questions.append(question)
        models.Question.objects.bulk_create(questions)

        for question in questions:
            question.tags.add(random.choice(tags))
        self.stdout.write("QUESTIONS FILLED\n")

        answers = []
        for i in range(ratio * 100):
            answer = models.Answer(text=fake.text(), question=random.choice(questions), user_profile=random.choice(profiles),
                                   is_correct=random.choice([True, False]))
            answers.append(answer)
        models.Answer.objects.bulk_create(answers)
        self.stdout.write("ANSWERS FILLED\n")

        like_questions = []
        for profile in profiles:
            for question in questions:
                if len(like_questions) >= ratio * 100:
                    break
                like_questions.append(models.LikedQuestions(user_profile=profile, question=question))

        models.LikedQuestions.objects.bulk_create(like_questions)

        self.stdout.write("QUESTIONS LIKES FILLED\n")

        like_answers = []
        for profile in profiles:
            for answer in answers:
                if len(like_answers) >= ratio * 100:
                    break
                like_answers.append(models.LikedAnswers(user_profile=profile, answer=answer))

        models.LikedAnswers.objects.bulk_create(like_answers)

        self.stdout.write("ANSWER LIKES FILLED\n")

        self.stdout.write("DONE")
