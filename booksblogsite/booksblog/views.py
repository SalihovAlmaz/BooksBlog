from django.http import JsonResponse
from rest_framework import viewsets, permissions
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404

from .models import Book, ReadingStatus, Review, Genres, Tags
from .serializers import BookSerializer, ReadingStatusSerializer, ReviewSerializer, GenresSerializer, TagsSerializer
from .permissions import IsOwnerOrAdmin, IsAdminOnly

class BookPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrAdmin]  # Применяем кастомное разрешение
    pagination_class = BookPagination
    filterset_fields = ['title', 'author', 'genres']
    search_fields = ['title', 'author__username', 'description']
    ordering_fields = ['time_create', 'title']
    ordering = ['-time_create']

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=False, methods=['get'])
    def filters(self, request):
        return JsonResponse({
            'genres': [{'slug': 'fantasy', 'name': 'Фэнтези'}],
            'tags': [{'slug': 'magic', 'name': 'Магия'}]
        })

class ReadingStatusViewSet(viewsets.ModelViewSet):
    serializer_class = ReadingStatusSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]  # Применяем кастомное разрешение

    def get_queryset(self):
        return ReadingStatus.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        book = get_object_or_404(Book, pk=self.request.data.get('book'))
        serializer.save(user=self.request.user, book=book)

class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]  # Применяем кастомное разрешение

    def get_queryset(self):
        book_id = self.kwargs.get('book_id')
        return Review.objects.filter(book_id=book_id)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        # Обновляем рейтинг книги после удаления отзыва
        book = instance.book
        instance.delete()
        book.update_average_rating()

    def perform_update(self, serializer):
        # Обновляем рейтинг книги после изменения отзыва
        serializer.save()
        instance = self.get_object()
        instance.book.update_average_rating()

class GenresViewSet(viewsets.ModelViewSet):
    queryset = Genres.objects.all()
    serializer_class = GenresSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAdminOnly]  # Применяем разрешение для админов

class TagsViewSet(viewsets.ModelViewSet):
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAdminOnly]  # Применяем разрешение для админов