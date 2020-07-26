from django import forms
from .models import Post

from django.forms import ModelForm
from posts.models import Comment


class PostForm(forms.ModelForm):
    
    class Meta:
        model = Post
        fields = ('group', 'text', 'image')
        help_texts = {'group': 'Выберете группу', 'text': 'Введите текст'}


class CommentForm(ModelForm):
    class Meta(object):
        model = Comment
        fields = ['text']
