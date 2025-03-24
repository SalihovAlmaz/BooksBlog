from django.contrib.auth import get_user_model
from django.core.validators import MinLengthValidator
from django.db import models
from django.db.models import Avg
from django.urls import reverse
from django.contrib.auth.models import User


class Book(models.Model):

    title = models.CharField(max_length=255,verbose_name='Название')
    author = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, related_name='books', null=True, blank=True, verbose_name='Автор')
    description = models.TextField(blank=True,verbose_name='Описание')
    time_create = models.DateTimeField(auto_now_add=True,verbose_name='Время создания',validators=[MinLengthValidator(5,message='Минимум 5 символов')])
    time_update = models.DateTimeField(auto_now=True,verbose_name='Время изменения')
    photo = models.ImageField(upload_to='photos/%Y/%m/%d/',default=None,blank=True,null=True,verbose_name='Фото')
    slug = models.SlugField(max_length=255,unique=True, db_index=True,verbose_name='Слаг')
    genres = models.ForeignKey('Genres', on_delete=models.PROTECT,related_name='book',verbose_name='Жанры')
    tags = models.ManyToManyField('Tags',blank=True, related_name='tags',verbose_name="Теги")




    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Список книг'
        verbose_name_plural = 'Список книг'
        ordering = ['-time_create']
        indexes = [
            models.Index(fields=['-time_create'])
        ]

    def get_absolute_url(self):
        return reverse('post',kwargs={'post_slug': self.slug})

    def update_average_rating(self):
        """Метод для обновления среднего рейтинга книги"""
        average_rating = Review.objects.filter(book=self).aggregate(Avg('rating'))['rating__avg']
        self.average_rating = average_rating if average_rating else None
        self.save()


class Genres(models.Model):
    name = models.CharField(max_length=100, db_index=True,verbose_name="Жанр")
    slug = models.SlugField(max_length=255,unique=True,db_index=True)

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('genres',kwargs={'genres_slug': self.slug})


class Tags (models.Model):
    name = models.CharField(max_length =100,db_index=True)
    slug = models.SlugField(max_length=255, unique=True,db_index=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('name',kwargs={'name_slug': self.slug})

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class ReadingStatus(models.Model):
    READING = 'reading'
    FINISHED = 'finished'
    WISH_LIST = 'wish_list'
    STATUS_CHOICES = [
        (READING, 'Reading'),
        (FINISHED, 'Finished'),
        (WISH_LIST, 'Wish List'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Связь с пользователем
    book = models.ForeignKey(Book, on_delete=models.CASCADE)  # Связь с книгой
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=READING)  # Статус чтения
    start_date = models.DateField(null=True, blank=True)  # Дата начала чтения
    finish_date = models.DateField(null=True, blank=True)  # Дата завершения чтения

    def __str__(self):
        return f'{self.user.username} - {self.book.title} - {self.status}'

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Связь с пользователем
    book = models.ForeignKey(Book, on_delete=models.CASCADE)  # Связь с книгой
    review_text = models.TextField()  # Текст рецензии
    rating = models.PositiveIntegerField()  # Рейтинг книги (например, от 1 до 5)
    created_at = models.DateTimeField(auto_now_add=True)  # Дата создания рецензии

    class Meta:
        unique_together = ['user', 'book']  # Один пользователь может оставить только одну рецензию на книгу

    def __str__(self):
        return f'Review by {self.user.username} on {self.book.title}'

