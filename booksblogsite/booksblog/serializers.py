from rest_framework import serializers
from .models import Book, Genres, Tags, ReadingStatus, Review, Author
from django.contrib.auth import get_user_model

class BookSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.username', read_only=True)
    genres_name = serializers.CharField(source='cat.name', read_only=True)
    genres = serializers.StringRelatedField(many=True, source='genre.name')  # Список жанров

    class Meta:
        model = Book
        fields = ['id', 'title', 'author_name', 'description', 'time_create', 'time_update', 'photo', 'slug', 'genres_name', 'genres']
        read_only_fields = ['time_create', 'time_update']

    def validate_title(self, value):
        if len(value) < 5:
            raise serializers.ValidationError("Название книги должно быть не менее 5 символов.")
        return value


class ReadingStatusSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username', read_only=True)  # Имя пользователя
    book_title = serializers.CharField(source='book.title', read_only=True)  # Название книги
    status_display = serializers.CharField(source='get_status_display', read_only=True)  # Читаемый статус (display value)

    class Meta:
        model = ReadingStatus
        fields = ['id', 'user', 'book', 'book_title', 'status', 'status_display', 'start_date', 'finish_date']
        read_only_fields = ['user', 'book', 'status_display']  # Эти поля не должны быть изменяемыми через API

    def validate(self, attrs):
        # Проверяем, чтобы дата завершения не была раньше даты начала
        if attrs.get('finish_date') and attrs.get('start_date') and attrs['finish_date'] < attrs['start_date']:
            raise serializers.ValidationError('Дата завершения не может быть раньше даты начала.')
        return attrs

class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username', read_only=True)  # Имя пользователя
    book_title = serializers.CharField(source='book.title', read_only=True)  # Название книги

    class Meta:
        model = Review
        fields = ['id', 'user', 'book', 'book_title', 'review_text', 'rating', 'created_at']
        read_only_fields = ['user', 'book', 'created_at']

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Рейтинг должен быть от 1 до 5.")
        return value

    def validate(self, attrs):
        user = self.context['request'].user
        book = attrs['book']

        # Проверяем, что у пользователя нет рецензии на эту книгу
        if Review.objects.filter(user=user, book=book).exists():
            raise serializers.ValidationError("Вы уже оставили рецензию на эту книгу.")
        return attrs

class GenresSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genres
        fields = ['id', 'name', 'slug']
        read_only_fields = ['id']

class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = ['id', 'genre', 'slug']
        read_only_fields = ['id']


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['id', 'name', 'biography', 'birth_date', 'death_date', 'photo']
