from django.urls import path

from parser_books.views import BookViewSet

app_name = 'parser_books'

urlpatterns = [
    path(
        '',
        BookViewSet.as_view({'get': 'list'}),
        name='list_book',
    ),
    path(
        'create/',
        BookViewSet.as_view({'post': 'create'}),
        {'action': 'id'},
        name='create_book',
    ),
    path(
        '<int:pk>',
        BookViewSet.as_view({'get': 'retrieve'}),
        name='book_by_id',
    ),
    path(
        'update-all/',
        BookViewSet.as_view({'get': 'update_all'}),
        name='update_all',
    ),
    path(
        'test_for_work/',
        BookViewSet.as_view({'get': 'test_for_work'}),
        name='test_for_work',
    ),
    path(
        'delete-all/',
        BookViewSet.as_view({'get': 'delete_all'}),
        name='delete_all',
    )
]
