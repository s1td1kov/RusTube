from django.forms import ModelForm

from .models import Comment, Post


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['group', 'text', 'image', ]
        labels = {
            'group': 'Сообщество',
            'text': 'Текст записи',
            'image': 'Картинка',
        }


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['text', ]
        labels = {
            'text': 'Текст комментария',
        }
