from django.db import models
from django.contrib.auth import get_user_model
from core.models import PubDateModel
from django.db.models.deletion import CASCADE

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200,
                             verbose_name='Название группы',
                             help_text='Назовите группу')
    slug = models.SlugField(unique=True,
                            verbose_name='Обозначение группы',
                            help_text='Присвойте группе ярлык')
    description = models.TextField(
        verbose_name='Описание группы',
        help_text='Дайте группе краткое описание')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'


class Post(PubDateModel):

    text = models.TextField(verbose_name='Текст поста',
                            help_text='Текст поста')
    group = models.ForeignKey(Group, on_delete=models.SET_NULL,
                              related_name='posts',
                              blank=True, null=True,
                              verbose_name='Группа',
                              help_text='Группа'
                              )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
        help_text='Автор')

    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True)

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.text[:15]


class Comment(PubDateModel):
    post = models.ForeignKey(
        Post,
        related_name='comments',
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        User,
        related_name='comments',
        on_delete=models.SET_NULL,
        null=True
    )
    text = models.TextField('text', help_text='comment text')

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return f"Запись: '{self.post}', автор: '{self.author}'"


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=CASCADE,
        related_name="follower"
    )
    author = models.ForeignKey(
        User,
        on_delete=CASCADE,
        related_name="following"
    )

    def __str__(self):
        return self.text

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("user", "author"),
                name="unique_pair"
            ),
        ]
