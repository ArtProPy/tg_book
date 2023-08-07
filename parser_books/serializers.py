from rest_framework import serializers

from parser_books.models import *


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = '__all__'


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'


class BookFullSerializer(serializers.ModelSerializer):
    authors = serializers.SerializerMethodField(read_only=True)
    genres = serializers.SerializerMethodField(read_only=True)
    series = serializers.SerializerMethodField(read_only=True)

    @staticmethod
    def get_authors(obj):
        return [AuthorSerializer(author).data for author in obj.authors.all()]

    @staticmethod
    def get_genres(obj):
        return [GenreSerializer(genres).data for genres in obj.genres.all()]

    @staticmethod
    def get_series(obj):
        return SeriesSerializer(obj.series).data

    class Meta:
        model = Book
        fields = '__all__'


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = '__all__'


class SeriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Series
        fields = '__all__'


class BookCreateSerializer(serializers.ModelSerializer):
    authors = serializers.SerializerMethodField(read_only=True)
    genres = serializers.SerializerMethodField(read_only=True)
    series = serializers.SerializerMethodField(read_only=True)
    status = serializers.ChoiceField(
        choices=[x[0] for x in BOOK_STATUS],
        default='default'
    )

    @staticmethod
    def get_authors(obj):
        return [AuthorSerializer(author).data for author in obj.authors.all()]

    @staticmethod
    def get_genres(obj):
        return [GenreSerializer(genres).data for genres in obj.genres.all()]

    @staticmethod
    def get_series(obj):
        return SeriesSerializer(obj.series).data

    def validate(self, attrs):
        attrs = super().validate(attrs)

        if self.initial_data.get('image_url'):
            attrs['image'] = self.initial_data['image_url']

        if self.initial_data.get('series_name'):
            attrs['series'] = Series.objects.get_or_create(
                name=self.initial_data['series_name']
            )[0]
        if self.initial_data.get('authors_name'):
            attrs['authors'] = [
                Author.objects.get_or_create(name=author)[0].id
                for author in self.initial_data['authors_name']
            ]
        if self.initial_data.get('genres_name'):
            attrs['genres'] = [
                Genre.objects.get_or_create(name=genre)[0].id
                for genre in self.initial_data['genres_name']
            ]

        return attrs

    class Meta:
        model = Book
        fields = '__all__'
        # swagger_schema_fields = {
        #     "type": openapi.TYPE_OBJECT,
        #     "title": "Email",
        #     "properties": {
        #         "subject": openapi.Schema(
        #             title="Email subject",
        #             type=openapi.TYPE_STRING,
        #         ),
        #         "body": openapi.Schema(
        #             title="Email body",
        #             type=openapi.TYPE_STRING,
        #         ),
        #     },
        #     "required": ["subject", "body"],
        # }


class AsyncBookCreateSerializer(serializers.ModelSerializer):
    authors = serializers.SerializerMethodField()
    genres = serializers.SerializerMethodField()
    series_name = serializers.SerializerMethodField()
    # status = serializers.ChoiceField(choices=[x[0] for x in BOOK_STATUS])

    def get_authors(self, obj):
        obj.authors.set(
            [
                Author.objects.get_or_create(name=author)[0]
                for author in self.initial_data['authors']
            ]
        )
        return [AuthorSerializer(author).data for author in obj.authors.all()]

    def get_genres(self, obj):
        if self.initial_data.get('genres'):
            obj.genres.set(
                [
                    Genre.objects.get_or_create(name=genre)[0].id
                    for genre in self.initial_data['genres']
                ]
            )
        return [GenreSerializer(genre).data for genre in obj.genres.all()]

    def get_series_name(self, obj):
        if self.initial_data.get('series'):
            obj.series = Series.objects.get_or_create(name=self.initial_data['series'])[0]
        return SeriesSerializer(obj.series).data

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if self.initial_data.get('image_url'):
            attrs['image'] = self.initial_data['image_url']
        if self.initial_data.get('series_name'):
            attrs['series'] = Series.objects.get_or_create(
                name=self.initial_data['series_name']
            )[0]

        return attrs

    class Meta:
        model = Book
        fields = '__all__'
