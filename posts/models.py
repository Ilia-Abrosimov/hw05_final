from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200, verbose_name="Наименование")
    slug = models.SlugField(unique=True)
    description = models.TextField(verbose_name="Описание")

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(verbose_name="Текст")
    pub_date = models.DateTimeField("Дата публикации", auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="posts", verbose_name="Автор")
    group = models.ForeignKey(Group, on_delete=models.SET_NULL,
                              blank=True, null=True, related_name="posts",
                              verbose_name="Группа")
    image = models.ImageField(upload_to='posts/', blank=True, null=True)

    class Meta:
        ordering = ['-pub_date']
        verbose_name_plural = 'Посты'


class Comment(models.Model):
    post = models.ForeignKey(Post,
                             on_delete=models.SET_NULL,
                             related_name="comments", blank=True, null=True,
                             verbose_name="Комментарий к посту",
                             help_text="Добавьте комментарий к посту")
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               verbose_name="Автор комментария",
                               related_name="comments",
                               help_text="Автор комментария")
    text = models.TextField(max_length=1000,
                            verbose_name="Комментарий к посту",
                            help_text="Текст комментария")
    created = models.DateTimeField("date published", auto_now_add=True)

    class Meta:
        ordering = ('created',)
