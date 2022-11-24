from rest_framework import serializers

from parser_books.models import *


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = '__all__'


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = '__all__'


class SeriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Series
        fields = '__all__'


class AuthorBookSerializer(serializers.ModelSerializer):
    author = AuthorSerializer()

    class Meta:
        model = AuthorBook
        fields = '__all__'


class GenreBookSerializer(serializers.ModelSerializer):
    genre = GenreSerializer()

    class Meta:
        model = GenreBook
        fields = '__all__'


class BookSerializer(serializers.ModelSerializer):
    genres = serializers.SerializerMethodField()
    series_name = serializers.StringRelatedField(
        source='series.name'
    )
    serializers.ManyRelatedField
    authors = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = '__all__'

    @staticmethod
    def get_authors(obj):
        return obj.authors.values_list('author__name', flat=True)

    @staticmethod
    def get_genres(obj):
        return obj.genres.values_list('genre__name', flat=True)

    @staticmethod
    def validate_genres(genre):
        print('+'*100)
        return genre

    def validate(self, attrs):
        attrs['series'] = Series.objects.get_or_create(name=self.initial_data['series__name'])[0] \
            if self.initial_data.get('series__name') \
            else None
        print('!' * 100)
        return attrs
