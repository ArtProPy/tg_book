from django.urls import path

from parser_books.views import BookViewSet

app_name = 'parser_books'

urlpatterns = [
    path(
        'update-all/',
        BookViewSet.as_view({'get': 'update_all'}),
        name='update_all',
    ),
]
