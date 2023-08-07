from django.contrib import admin
from django.db import models
from django.db.models import Count, F
from django.urls import reverse
from django.utils.html import format_html

from parser_books.forms import CustomAdminFileWidget
from parser_books.mixins import AdminListPrefetchRelatedMixin
from parser_books.models import Book, Author, Genre, Series


class BookInLine(admin.TabularInline):
    model = Book
    fields = ('book_link', 'status', 'image_preview', 'author_link')
    ordering = ('title', 'status')
    readonly_fields = fields
    extra = 0

    @staticmethod
    @admin.display(description=Author._meta.get_field('name').verbose_name.title())
    def author_link(obj):
        return format_html(''.join([u'<a href="{0}">{1}</a>'.format(
            reverse('admin:parser_books_author_change', args=(author.pk,)),
            author.name) for author in obj.authors.all()])
        )


# class BookNamesInLine(admin.TabularInline):
#     model = Book
#     fields = ('book_link_',)
#     readonly_fields = fields
#     extra = 0
#
#     @staticmethod
#     @admin.display(description=Book._meta.get_field('title').verbose_name.title())
#     def book_link_(obj):
#         # return format_html(''.join([u'<a href="{0}">{1}</a>'.format(
#         #     reverse('admin:parser_books_author_change', args=(author.pk,)),
#         #     author.name) for author in obj.series.book_set.all().exclude(obj)])
#         # )
#         return None


@admin.register(Book)
class BookAdmin(AdminListPrefetchRelatedMixin, admin.ModelAdmin):
    list_select_related = ('series',)
    list_prefetch_related = ('authors', 'genres')
    list_display = (
        'title', 'get_authors', 'series', 'series_num', 'status', 'image_preview'
    )
    ordering = ('title', )
    search_fields = ('title', 'series__name', 'authors__name', 'genres__name')
    fieldsets = (
        (None, {
            'fields': ('title', 'authors', 'image')
        }),
        ('Дополнительные данные', {
            'classes': ('collapse',),
            'fields': ('description', 'genres', 'series', 'series_num', 'status'),
        }),
    )
    # inlines = (BookNamesInLine,)

    # Images 1
    formfield_overrides = {
        models.ImageField: {"widget": CustomAdminFileWidget}
    }

    @admin.display(description='Авторы')
    def get_authors(self, obj):
        return [author for author in obj.authors.all()]


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name',)
    ordering = ('name',)


@admin.register(Genre)
class GenreAdmin(AdminListPrefetchRelatedMixin, admin.ModelAdmin):
    list_display = ('name', 'count_books')
    list_prefetch_related = ('books', )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(
            _count_books=Count('books', distinct=True)
        ).order_by('-_count_books', 'name')

    @staticmethod
    @admin.display(description='Книг')
    def count_books(obj):
        return obj.books.count()


@admin.register(Series)
class SeriesAdmin(AdminListPrefetchRelatedMixin, admin.ModelAdmin):
    search_fields = ('name', )
    list_display = ('name', 'count_books', 'last_book')
    inlines = (BookInLine,)
    list_prefetch_related = ('books',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(
            _count_books=Count('books', distinct=True),
        ).order_by('-_count_books', 'name')
