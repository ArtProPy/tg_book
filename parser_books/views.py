import datetime
from async_drf.viewsets import AsyncModelViewSet
from django.core.paginator import Paginator
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from parser_books import serializers
from parser_books.decorators import query_debugger
from parser_books.helper import ParserAsync
from parser_books.models import Book, Author, Genre, Series
from parser_books.paginators import StandardResultsSetPagination
from parser_books.parser import run_parser

mapper = {
    'book': {
        'list': serializers.BookFullSerializer,
        'create': serializers.BookCreateSerializer
    }
}


class BookViewSet(ModelViewSet):
    serializer_class = serializers.BookSerializer
    queryset = Book.objects.select_related('series').prefetch_related('authors') \
        .prefetch_related('genres')
    pagination_class = StandardResultsSetPagination
    filterset_fields = '__all__'

    authors = openapi.Parameter(
        'authors_name',
        in_=openapi.IN_QUERY,
        description='Список авторов',
        type=openapi.TYPE_ARRAY,
        required=False,
        items=[openapi.TYPE_STRING]
    )
    genres = openapi.Parameter(
        'genres_name',
        in_=openapi.IN_QUERY,
        description='Список жанров',
        type=openapi.TYPE_ARRAY,
        required=False,
        items=[openapi.TYPE_STRING]
    )
    series = openapi.Parameter(
        'series_name',
        in_=openapi.IN_QUERY,
        description='Название серии книг',
        type=openapi.TYPE_STRING,
        required=False
    )
    image = openapi.Parameter(
        'image_url',
        in_=openapi.IN_QUERY,
        description='Путь к изображению',
        type=openapi.TYPE_STRING,
        required=False,
        format='image/image_name.jpg'
    )

    def get_serializer_class(self):
        dict_serializers = mapper.get(self.queryset.model._meta.model_name, {})
        return dict_serializers.get(self.action, self.serializer_class)

    @swagger_auto_schema(
        operation_summary='Создать новую книгу',
        operation_description='передаёт данные для создания книги',
        tags=['Книги', 'Создание'],
        manual_parameters=[authors, genres, series, image]
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Получить книгу по id',
        operation_description='Получает книгу по её идентификатору',
        tags=['Книги'],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @query_debugger
    @swagger_auto_schema(
        operation_summary='Получить список книг',
        operation_description='Получает список всех книг',
        tags=['Книги'],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def update_all(self, request, *args, **kwargs):
        s_time = datetime.datetime.now()
        run_parser()
        print(f'update_all: {datetime.datetime.now() - s_time}')
        self.count()
        return Response()

    def test(self, request, *args, **kwargs):
        self.delete_all(request, *args, **kwargs)
        data = {}
        for step in [20, 20, 20, 20, 20, 20]:
            times = []
            for _ in range(5):
                s_time = datetime.datetime.now()
                run_parser(all=False, last_page=5)
                times.append(datetime.datetime.now() - s_time)
                self.delete_all(request, *args, **kwargs)
            [print(f'new {idx + 1}: {time}') for idx, time in enumerate(times)]
            print(f'\nИтого new: {sum([date for date in times], datetime.timedelta()) / len(times)}\n')
            times = []
            for _ in range(5):
                s_time = datetime.datetime.now()

                parser = ParserAsync(step=step)
                parser.run(all=False, last_page=5)
                times.append(datetime.datetime.now() - s_time)
                self.delete_all(request, *args, **kwargs)
            [print(f'old {idx + 1}: {time}') for idx, time in enumerate(times)]
            print(f'\nИтого old: {sum([date for date in times], datetime.timedelta()) / len(times)}\n')
            # print(sum(times) / len(times))

        return Response()

    def test_for_work(self, request, *args, **kwargs):
        data_list = [
            {
                'step': [20],
                'repetition': 5,
                'pages': 5,
                'method': [
                    {
                        'func': self.new_method,
                        'times': [],
                        'result': ''
                    },{
                        'func': self.old_method,
                        'times': [],
                        'result': ''
                    }
                ]
            }
        ]
        for data in data_list:
            for step in data['step']:
                for _ in range(data['repetition']):
                    for info in data['method']:
                        s_time = datetime.datetime.now()
                        info['func'](step=step, last_page=data['pages'])
                        info['times'].append(datetime.datetime.now() - s_time)

                    info['result'] = sum([date for date in info['times']], datetime.timedelta()) / len(info['times'])


        return Response()

    @staticmethod
    def new_method(step, last_page):
        run_parser(all=False, last_page=5)

    @staticmethod
    def old_method(step, last_page):
        parser = ParserAsync(step=step)
        parser.run(all=False, last_page=5)

    def count(self):
        print(f'Book: {Book.objects.count()}')
        print(f'Series: {Series.objects.count()}')
        print(f'Genre: {Genre.objects.count()}')
        print(f'Author: {Author.objects.count()}')

    def delete_all(self, request, *args, **kwargs):
        self.count()
        Author.objects.all().delete()
        print('Authors is deleted')
        Genre.objects.all().delete()
        print('Genres is deleted')
        Series.objects.all().delete()
        print('Series is deleted')
        Book.objects.all().delete()
        print('Books is deleted')
        return Response()


class AsyncBookViewSet(AsyncModelViewSet):
    serializer_class = serializers.BookSerializer
    queryset = Book.objects.all()
    filterset_fields = '__all__'

    def get_serializer_class(self):
        dict_serializers = mapper.get(self.queryset.model._meta.model_name, {})
        return dict_serializers.get(self.action, self.serializer_class)

    # async def create(self, request, *args, **kwargs):
    #     return super().create(request, *args, **kwargs)

