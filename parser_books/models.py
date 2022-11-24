from django.db import models


class Author(models.Model):
    name = models.CharField('ФИО автора', max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Автор'
        verbose_name_plural = 'Авторы'


class Genre(models.Model):
    name = models.CharField('Название жанра', max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Series(models.Model):
    name = models.CharField('Название серии', max_length=255)
    status = models.CharField('Статус Серии', max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Серия'
        verbose_name_plural = 'Серии'


class Book(models.Model):
    num_book = models.PositiveIntegerField('Номер книги на сайте', blank=True, null=True)
    title = models.CharField('Название книги', max_length=255)
    description = models.TextField('Описание книги', blank=True, null=True)
    series = models.ForeignKey(
        Series,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='books'
    )
    img_src = models.ImageField(
        'Изображение', upload_to=f'.images/{series.name if series.name else "no_series"}', default=None
    )
    series_num = models.IntegerField('Номер книги в серии', blank=True, null=True)
    status = models.CharField('Статус книги', max_length=255, blank=True, null=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Книга'
        verbose_name_plural = 'Книги'


class GenreBook(models.Model):
    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE,
        related_name='books'
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='genres'
    )

    def __str__(self):
        return f'{self.genre.name}: {self.book.title}'

    class Meta:
        verbose_name = 'Жанр-Книга'
        verbose_name_plural = 'Жанры-Книги'


class AuthorBook(models.Model):
    author = models.ForeignKey(
        Author,
        on_delete=models.CASCADE,
        related_name='books'
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='authors'
    )

    def __str__(self):
        return f'{self.author.name}: {self.book.title}'

    class Meta:
        verbose_name = 'Автор-Книга'
        verbose_name_plural = 'Авторы-Книги'
