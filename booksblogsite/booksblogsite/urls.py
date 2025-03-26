from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from booksblog.views import BookViewSet, ReadingStatusViewSet, ReviewViewSet, GenresViewSet, TagsViewSet

router = DefaultRouter()
router.register(r'books', BookViewSet, basename='book')
router.register(r'reading-status', ReadingStatusViewSet, basename='reading-status')
router.register(r'books/(?P<book_id>[^/.]+)/reviews', ReviewViewSet, basename='review')
router.register(r'genres', GenresViewSet, basename='genre')
router.register(r'tags', TagsViewSet, basename='tag')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
##    path('api/filters/', filters, name='filters'),
]
