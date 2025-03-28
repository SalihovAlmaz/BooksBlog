from rest_framework import serializers
from .models import Book, Genres, Tags, ReadingStatus, Review
from django.contrib.auth import get_user_model


class GenresSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genres
        fields = ['id', 'name', 'slug']
        read_only_fields = ['id']


class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = ['id', 'name', 'slug']
        read_only_fields = ['id']


class BookSerializer(serializers.ModelSerializer):
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    author_display = serializers.StringRelatedField(source='author', read_only=True)
    genres = GenresSerializer(read_only=True)
    tags = TagsSerializer(many=True, read_only=True)
    average_rating = serializers.FloatField(read_only=True)

    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'author_display', 'description',
                  'time_create', 'time_update', 'photo', 'slug', 'tags', 'genres', 'average_rating']
        read_only_fields = ['time_create', 'time_update']

    def validate_title(self, value):
        if len(value) < 5:
            raise serializers.ValidationError("Название книги должно быть не менее 5 символов.")
        return value


class ReadingStatusSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username', read_only=True)
    book_title = serializers.CharField(source='book.title', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = ReadingStatus
        fields = ['id', 'user', 'book', 'book_title', 'status', 'status_display', 'start_date', 'finish_date']
        read_only_fields = ['user', 'book', 'status_display']

    def validate(self, attrs):
        if attrs.get('finish_date') and attrs.get('start_date') and attrs['finish_date'] < attrs['start_date']:
            raise serializers.ValidationError('Дата завершения не может быть раньше даты начала.')
        return attrs


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username', read_only=True)
    book_title = serializers.CharField(source='book.title', read_only=True)

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
        book_slug = self.context['view'].kwargs.get('slug')

        if not book_slug:
            raise serializers.ValidationError("Не указан slug книги.")

        book = Book.objects.filter(slug=book_slug).first()
        if not book:
            raise serializers.ValidationError("Книга не найдена.")

        if Review.objects.filter(user=user, book=book).exists():
            raise serializers.ValidationError("Вы уже оставили рецензию на эту книгу.")

        attrs['book'] = book
        return attrs


User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    books = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
    reading_status = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'books', 'reading_status']

    def get_books(self, obj):
        books = Book.objects.filter(author=obj)
        return [{'id': book.id, 'title': book.title, 'slug': book.slug} for book in books]

    def get_role(self, obj):
        if obj.is_staff:
            return "admin"
        return "author"

    def get_reading_status(self, obj):
        statuses = ReadingStatus.objects.filter(user=obj)
        return [{
            'book': status.book.title,
            'status': status.get_status_display(),
            'start_date': status.start_date,
            'finish_date': status.finish_date
        } for status in statuses]
