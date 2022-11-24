from django.contrib import admin

from parser_books.models import Book, Author, Genre, Series, GenreBook, AuthorBook


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'authors', 'series', 'series_num', 'status')
    ordering = ('authors', 'series', 'title')

    def authors(self, obj):
        return [author.author for author in obj.authors.all()]


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name',)
    ordering = ('name',)


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name',)
    ordering = ('name',)


@admin.register(Series)
class SeriesAdmin(admin.ModelAdmin):
    list_display = ('name', 'status')
    ordering = ('name', 'status')


@admin.register(GenreBook)
class GenreBookAdmin(admin.ModelAdmin):
    list_display = ('book', 'genre')
    ordering = ('genre', 'book')


@admin.register(AuthorBook)
class AuthorBookAdmin(admin.ModelAdmin):
    list_display = ('book', 'author')
    ordering = ('author', 'book')
