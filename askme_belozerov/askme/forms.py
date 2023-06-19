# from django import forms
# from .models import User, Question, Tag, Answer
from django.contrib.auth.models import User
# from django.core.exceptions import ValidationError


from django import forms
from django.forms.utils import ErrorList
from django.contrib.auth.models import User
from askme import models
from django.contrib import messages


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class SettingForm(forms.Form):
    username = forms.CharField(required=False)
    email = forms.EmailField(required=False, widget=forms.EmailInput)
    password = forms.CharField(required=True, min_length=8, widget=forms.PasswordInput)
    password_check = forms.CharField(required=True, min_length=8, widget=forms.PasswordInput)
    new_password = forms.CharField(required=False, min_length=8, widget=forms.PasswordInput)
    new_password_check = forms.CharField(required=False, min_length=8, widget=forms.PasswordInput)
    avatar = forms.ImageField(required=False, widget=forms.FileInput)

    def clean_username(self):
        username = self.cleaned_data.get('username')

        if username and models.User.objects.filter(username=username).exists():
            self.add_error('username', 'This username is already taken.')

        return username

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        new_password_check = cleaned_data.get('new_password_check')
        password = cleaned_data.get('password')
        password_check = cleaned_data.get('password_check')

        if new_password and new_password != new_password_check:
            self.add_error('new_password', '')
            self.add_error('new_password_check', "New password fields don't match.")

        if password and password != password_check:
            self.add_error('password', '')
            self.add_error('password_check', "Password fields don't match.")

        return cleaned_data

    def save(self, request):
        user = models.User.objects.get(username=request.user)
        profile = models.Profile.objects.get(profile=user)
        username = self.cleaned_data.get('username')
        email = self.cleaned_data.get('email')
        new_password = self.cleaned_data.get('new_password')
        avatar = self.cleaned_data.get('avatar')

        if new_password:
            user.set_password(new_password)

        if username:
            profile.username = username
            user.username = username

        if email:
            user.email = email

        if avatar:
            profile.avatar = avatar

        user.save()
        profile.save()
        messages.success(request, 'Profile updated successfully!')

class AnswerForm(forms.Form):
    answer = forms.CharField(required=True, max_length=500,
                             widget=forms.Textarea(attrs={'placeholder': 'Enter an answer...'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['answer'].label = ''

    def save(self, request, question_id):
        user = models.User.objects.get(username=request.user)
        profile = models.Profile.objects.get(profile=user)
        question = models.Question.objects.get(id=question_id)
        answer = self.cleaned_data['answer']

        answer_obj = models.Answer.objects.create(text=answer, question=question, user_profile=profile)
        messages.success(request, 'Thanks for your answer!')

        return answer_obj


class QuestionForm(forms.ModelForm):
    title = forms.CharField(max_length=50)
    text = forms.CharField(max_length=500, widget=forms.Textarea)
    tags = forms.CharField(required=False)
    tag = forms.ModelMultipleChoiceField(queryset=models.Tag.objects.all(), required=False)

    def save(self, profile):
        super().clean()
        tags_names = []
        if self.cleaned_data['tags']:
            tags_names.extend(self.cleaned_data['tags'].split(','))
        if self.cleaned_data['tag']:
            tags_names.extend([tag.name for tag in self.cleaned_data['tag']])

        tags = []
        for tag_name in tags_names:
            if models.Tag.objects.filter(name=tag_name).exists():
                tags.append(models.Tag.objects.get(name=tag_name))
            else:
                new_tag = models.Tag(name=tag_name)
                new_tag.save()
                tags.append(new_tag)

        new_question = models.Question.objects.create(user_profile=profile,
                                        name=self.cleaned_data['title'],
                                        text=self.cleaned_data['text'])
        new_question.tags.set(tags)
        return new_question

    class Meta:
        model = models.Question
        fields = ['title', 'text', 'tags', 'tag']
