import time

from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from parser_books.helper import ParserAsync
from parser_books.models import Book, Author, AuthorBook, Genre, GenreBook
from parser_books.serializers import BookSerializer


class BookViewSet(ModelViewSet):
    serializer_class = BookSerializer
    queryset = Book.objects.all()
    filterset_fields = '__all__'

    def perform_create(self, serializer):
        book = serializer.save()
        for author in serializer.initial_data['authors']:
            AuthorBook.objects.create(author=Author.objects.get_or_create(name=author)[0], book=book)
        for genre in serializer.initial_data['genres']:
            GenreBook.objects.create(genre=Genre.objects.get_or_create(name=genre)[0], book=book)

    def update_all(self, request, *args, **kwargs):
        # url = 'https://litrpg.ru/'
        # parser = Parser(url, from_page=1, to_page=1)
        # books = parser.get_books_data()
        # [print(book) for book in books]
        for step in [25]:
            print()
            print('='*100)
            print(f'step = {step}')
            s_time = time.time()
            parser = ParserAsync(step=step)
            parser.run()
            print(time.time() - s_time)
            print('=' * 100)

        return Response()
