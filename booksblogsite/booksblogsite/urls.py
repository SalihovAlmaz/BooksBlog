
from django.contrib import admin
from django.urls import path, include

from booksblog.views import BookListCreateView, BookDetailView, ReadingStatusListCreateView, ReadingStatusDetailView, \
    ReviewListCreateView, ReviewDeleteView, GenresListCreateView, GenresDetailView, TagsListCreateView, \
    TagsDetailView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('books/', BookListCreateView.as_view(), name='book-list-create'),
    path('books/<slug:slug>/', BookDetailView.as_view(), name='book-detail'),
    path('reading-status/', ReadingStatusListCreateView.as_view(), name='reading-status-list-create'),
    path('reading-status/<int:pk>/', ReadingStatusDetailView.as_view(), name='reading-status-detail'),
    path('books/<int:book_id>/reviews/', ReviewListCreateView.as_view(), name='review-list-create'),
    path('reviews/<int:pk>/', ReviewDeleteView.as_view(), name='review-delete'),
    path('categories/', GenresListCreateView.as_view(), name='category-list-create'),
    path('categories/<slug:cat_slug>/', GenresDetailView.as_view(), name='category-detail'),
    path('genres/', TagsListCreateView.as_view(), name='genre-list-create'),
    path('genres/<slug:genre_slug>/', TagsDetailView.as_view(), name='genre-detail'),
    path('', include('frontend.urls')),
]
