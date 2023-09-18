from django.forms import ModelForm, Textarea, Select, TextInput
from .models import Post, Response, Reply, Category
from django_ckeditor_5.widgets import CKEditor5Widget
from django import forms
from django.core.exceptions import ValidationError

def validate_file_extension(value):
    """
    Проверяет, что файл имеет разрешенное расширение.
    """
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.mp4', '.avi', '.pdf', '.doc', '.docx']
    ext = value.name.split('.')[-1].lower()
    if ext not in allowed_extensions:
        raise ValidationError('Выбранный файл имеет недопустимое расширение.')

class PostForm(ModelForm):
    media = forms.FileField(label='Здесь вы можете загрузить картинки, видео, файлы', required=False,
                            validators=[validate_file_extension])
    # в класс мета, как обычно, надо написать модель, по которой будет строиться форма и нужные нам поля. Мы уже делали что-то похожее с фильтрами.
    class Meta:
        model = Post
        fields = ['title', 'text', 'postCategory', 'media']
        widgets = {
                    'title': Textarea(attrs={'class': 'title_class'}),
                    'text': Textarea(attrs={'class': 'text_class'}),
        }

        labels = {
            'title': 'Заголовок',
            'text': 'Текст',
            'postCategory': 'Категория',
        }



# class PostCreateForm(ModelForm):
#     media = forms.FileField(label='Здесь вы можете загрузить картинки, видео, файлы', required=False,validators=[validate_file_extension])
#     class Meta:
#         model = Post
#         fields = ['title', 'text', 'author', 'postCategory', 'media']
#         widgets = {
#                     'title': Textarea(attrs={'class': 'title_class'}),
#                     'author': TextInput(attrs={'class': 'author_class'}),
#                     "text": Textarea(attrs={"class": "text_class"}),
#
#         }



class PostResponseForm(ModelForm):
    class Meta:
        model = Response
        fields = ['text']
        widgets = {
            'text': TextInput(attrs={'class': 'text_class'}),
        }

class ReplyForm(ModelForm):
    class Meta:
        model = Reply
        fields = ['text', ]
        widgets = {
            'text': TextInput(attrs={'class': 'text_class'}),
        }