from django import forms
from .models import User, Question, Tag, Answer
from django.contrib.auth.models import User as U
from django.core.exceptions import ValidationError

class LoginForm(forms.Form):
    nickname = forms.CharField(max_length = 30)
    password = forms.CharField(max_length = 100, widget = forms.PasswordInput)


class RegistrationForm(forms.Form):
    username = forms.CharField(max_length=30)
    name = forms.CharField(max_length=30)
    password = forms.CharField(widget=forms.PasswordInput)
    password_check = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_check = cleaned_data.get('password_check')
        username = cleaned_data.get('username')

        if password != password_check:
            raise ValidationError("Passwords do not match.")

        if U.objects.filter(username=username).exists():
            raise ValidationError("Username is already taken.")

        return cleaned_data

    def save(self, commit=True):
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']
        name = self.cleaned_data['name']
        user = U.objects.create_user(username=username, password=password)
        profile = User.objects.create(profile=user, nickname=name)
        return profile


class QuestionForm(forms.ModelForm):
    tags = forms.CharField(required=False)

    class Meta:
        model = Question
        fields = ['title', 'text', 'tags', 'tag']

    def save(self, profile):
        super().clean()
        tags = self.cleaned_data['tag'] or []
        tags_names = self.cleaned_data['tags'] or []
        tags_names.extend([tag.name for tag in tags])

        tag_objects = []
        for tag_name in tags_names:
            tag_name = tag_name.strip()
            if not tag_name:
                continue
            tag, created = Tag.objects.get_or_create(name=tag_name)
            tag_objects.append(tag)

        new_question = Question.objects.create(
            author=profile,
            title=self.cleaned_data['title'],
            text=self.cleaned_data['text']
        )
        new_question.tag.set(tag_objects)
        return new_question


class AnswerForm(forms.ModelForm):
    text = forms.CharField(max_length=500, widget=forms.Textarea)

    class Meta:
        model = Answer
        fields = ["text"]

    def save(self, profile, question):
        super().clean()
        new_answer = self.save(commit=False)
        new_answer.author = profile
        new_answer.question = question
        new_answer.save()
        return new_answer
