from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .models import Book, ReadingStatus, Review, Genres, Tags, Author
from .serializers import BookSerializer, ReadingStatusSerializer, ReviewSerializer, GenresSerializer, \
    TagsSerializer, AuthorSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter, OrderingFilter
from django.shortcuts import get_object_or_404

class BookPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class BookListCreateView(generics.ListCreateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = BookPagination
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ['title', 'author__username', 'description']
    ordering_fields = ['time_create', 'title']
    ordering = ['-time_create']

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)  # Сохраняем текущего пользователя как автора книги

class BookDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class ReadingStatusListCreateView(generics.ListCreateAPIView):
    queryset = ReadingStatus.objects.all()
    serializer_class = ReadingStatusSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Отображаем только статусы для текущего пользователя
        return ReadingStatus.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Добавляем текущего пользователя в статус чтения
        book = get_object_or_404(Book, pk=self.request.data.get('book'))
        serializer.save(user=self.request.user, book=book)


class ReadingStatusDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ReadingStatus.objects.all()
    serializer_class = ReadingStatusSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Отображаем только статусы для текущего пользователя
        return ReadingStatus.objects.filter(user=self.request.user)


class ReviewListCreateView(generics.ListCreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Возвращаем рецензии только для книги, указанной в URL
        book_id = self.kwargs['book_id']
        return Review.objects.filter(book_id=book_id)

    def perform_create(self, serializer):
        # Сохраняем рецензию с текущим пользователем
        serializer.save(user=self.request.user)


class ReviewDeleteView(generics.DestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Удаляем рецензию только для текущего пользователя
        return Review.objects.filter(user=self.request.user)

    def perform_destroy(self, instance):
        # После удаления рецензии обновляем средний рейтинг книги
        book = instance.book
        instance.delete()
        book.update_average_rating()


class GenresListCreateView(generics.ListCreateAPIView):
    queryset = Genres.objects.all()
    serializer_class = GenresSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Genres.objects.all()


class GenresDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Genres.objects.all()
    serializer_class = GenresSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class TagsListCreateView(generics.ListCreateAPIView):
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Tags.objects.all()


class TagsDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


# Представление для получения списка книг и создания новой книги
class BookListView(generics.ListCreateAPIView):
    queryset = Book.objects.all()  # Список всех книг
    serializer_class = BookSerializer  # Используем сериализатор BookSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]  # Позволяет анонимным пользователям читать, а зарегистрированным — создавать книги

    def perform_create(self, serializer):
        """Метод для создания книги, если нужно выполнить дополнительную логику"""
        serializer.save()  # Создаем книгу с помощью сериализатора


# Представление для получения, обновления и удаления книги
class BookDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Book.objects.all()  # Получаем конкретную книгу
    serializer_class = BookSerializer  # Используем сериализатор BookSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]  # Позволяет анонимным пользователям читать, а зарегистрированным — редактировать и удалять


# Представление для получения списка авторов и создания нового автора
class AuthorListView(generics.ListCreateAPIView):
    queryset = Author.objects.all()  # Список всех авторов
    serializer_class = AuthorSerializer  # Используем сериализатор AuthorSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]  # Позволяет анонимным пользователям читать, а зарегистрированным — создавать авторов

    def perform_create(self, serializer):
        """Метод для создания автора, если нужно выполнить дополнительную логику"""
        serializer.save()  # Создаем автора с помощью сериализатора


# Представление для получения, обновления и удаления автора
class AuthorDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Author.objects.all()  # Получаем конкретного автора
    serializer_class = AuthorSerializer  # Используем сериализатор AuthorSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]  # Позволяет анонимным пользователям читать, а зарегистрированным — редактировать и удалять
