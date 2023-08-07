from django.contrib import admin
from django.db import models
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

BOOK_STATUS = (
    ('Не известно', 'default'),
    ('В процессе', 'draft'),
    ('Закончена', 'finished'),
    ('Заморожен', 'frozen')
)

SERIES_STATUS = (
    ('Не известно', 'default'),
    ('В процессе', 'draft'),
    ('Есть незаконченные', 'not_finished'),
    ('Закончен', 'finished'),
    ('Заморожена', 'frozen')
)


class Author(models.Model):
    name = models.CharField('ФИО автора', max_length=255, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Автор'
        verbose_name_plural = 'Авторы'


class Genre(models.Model):
    name = models.CharField('Название жанра', max_length=255, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Series(models.Model):
    name = models.CharField('Название серии', max_length=255, unique=True)
    status = models.CharField(
        'Статус серии',
        choices=SERIES_STATUS,
        default='default',
        max_length=20,
        blank=True,
        null=True
    )

    @property
    @admin.display(description='Книг в серии')
    def count_books(self):
        return self.books.count()

    @property
    @admin.display(description='Последняя книга в серии')
    def last_book(self):
        return list(self.books.all())[-1].book_link

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Серия'
        verbose_name_plural = 'Серии'


class Book(models.Model):
    title = models.CharField('Название книги', max_length=255, unique=True)
    description = models.TextField('Описание книги', blank=True, null=True)
    series_num = models.PositiveIntegerField(
        'Номер книги в серии', default=0, blank=True, null=True
    )
    status = models.CharField(
        'Статус книги',
        choices=BOOK_STATUS,
        default='default',
        max_length=20
    )
    image = models.ImageField(
        'Изображение',
        upload_to='images/',
        default='images/default.jpg',
        blank=True,
        max_length=250
    )
    series = models.ForeignKey(
        Series,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name='books',
        verbose_name='Серия'
    )
    authors = models.ManyToManyField(
        Author, verbose_name='Авторы', blank=True, related_name='books'
    )
    genres = models.ManyToManyField(
        Genre, verbose_name='Жанры', blank=True, related_name='books'
    )

    @property
    def image_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url

    @admin.display(description=image.verbose_name.title())
    def image_preview(self):
        return mark_safe(f'<a href="{self.image_url}"><img src="{self.image_url}" width="auto" height="100px" /></a>')

    @admin.display(description=title.verbose_name.title())
    def book_link(self):
        return format_html(u'<a href="{0}">{1}</a>'.format(
            reverse('admin:parser_books_book_change', args=(self.pk,)),
            self.title)
        )

    def __str__(self):
        return self.title

    class Meta:
        unique_together = ('title', 'image')
        verbose_name = 'Книга'
        verbose_name_plural = 'Книги'


IMAGES_STATUS = (
    ('Не известно', 'default'),
    ('В процессе', 'draft'),
    ('Закончена', 'finished'),
    ('Заморожен', 'frozen')
)
