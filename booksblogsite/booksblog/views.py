from rest_framework import viewsets, permissions
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from .models import Book, ReadingStatus, Review, Genres, Tags
from .permissions import IsOwnerOrAdmin
from .serializers import BookSerializer, ReadingStatusSerializer, ReviewSerializer, GenresSerializer, TagsSerializer, \
    UserSerializer
from .serializers import RegisterSerializer


class BookPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrAdmin]
    pagination_class = BookPagination
    filterset_fields = ['title', 'author', 'genres']
    search_fields = ['title', 'author__username', 'description']
    ordering_fields = ['time_create', 'title']
    ordering = ['-time_create']
    lookup_field = 'slug'

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_destroy(self, instance):
        if not self.request.user.is_staff and instance.author != self.request.user:
            return Response({'error': 'Вы не можете удалить эту книгу'}, status=403)
        instance.delete()


class ReadingStatusViewSet(viewsets.ModelViewSet):
    serializer_class = ReadingStatusSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ReadingStatus.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        book = get_object_or_404(Book, pk=self.request.data.get('book'))
        serializer.save(user=self.request.user, book=book)

    def perform_destroy(self, instance):
        if not self.request.user.is_staff and instance.user != self.request.user:
            return Response({'error': 'Вы не можете удалить этот статус'}, status=403)
        instance.delete()


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        book_slug = self.kwargs.get('slug')
        return Review.objects.filter(book__slug=book_slug)

    def perform_create(self, serializer):
        book_slug = self.kwargs.get('slug')
        book = get_object_or_404(Book, slug=book_slug)
        serializer.save(user=self.request.user, book=book)
        book.update_average_rating()

    def perform_destroy(self, instance):
        book = instance.book
        instance.delete()
        book.update_average_rating()

    def perform_update(self, serializer):
        instance = self.get_object()
        serializer.save()
        instance.book.update_average_rating()


class GenresViewSet(viewsets.ModelViewSet):
    queryset = Genres.objects.all()
    serializer_class = GenresSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class TagsViewSet(viewsets.ModelViewSet):
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class RegisterView(CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
