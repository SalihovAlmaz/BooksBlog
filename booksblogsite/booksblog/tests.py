from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Book, ReadingStatus, Review
from datetime import date

class ReadingStatusTests(APITestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(username='testuser', password='password')
        self.book = Book.objects.create(title="Test Book", author="Author", description="Test description", published_date="2021-01-01")
        self.client.login(username='testuser', password='password')

    def test_create_reading_status(self):
        url = reverse('reading-status-list-create')
        data = {'book': self.book.id, 'status': 'reading', 'start_date': str(date.today())}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ReadingStatus.objects.count(), 1)

    def test_update_reading_status(self):
        status_obj = ReadingStatus.objects.create(user=self.user, book=self.book, status='reading', start_date=date.today())
        url = reverse('reading-status-detail', kwargs={'pk': status_obj.id})
        data = {'status': 'finished', 'finish_date': str(date.today())}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        status_obj.refresh_from_db()
        self.assertEqual(status_obj.status, 'finished')

    def test_delete_reading_status(self):
        status_obj = ReadingStatus.objects.create(user=self.user, book=self.book, status='reading', start_date=date.today())
        url = reverse('reading-status-detail', kwargs={'pk': status_obj.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ReadingStatus.objects.count(), 0)

    def test_invalid_finish_date(self):
        url = reverse('reading-status-list-create')
        data = {'book': self.book.id, 'status': 'finished', 'start_date': str(date.today()), 'finish_date': str(date.today())}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('finish_date', response.data)

class ReviewTests(APITestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(username='testuser', password='password')
        self.book = Book.objects.create(title="Test Book", author="Author", description="Test description", published_date="2021-01-01")
        self.client.login(username='testuser', password='password')

    def test_create_review(self):
        url = reverse('review-list-create', kwargs={'book_id': self.book.id})
        data = {'review_text': 'Great book!', 'rating': 5}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Review.objects.count(), 1)
        self.assertEqual(self.book.average_rating, 5.0)

    def test_create_review_duplicate(self):
        Review.objects.create(user=self.user, book=self.book, review_text="Good book", rating=4)
        url = reverse('review-list-create', kwargs={'book_id': self.book.id})
        data = {'review_text': 'Amazing!', 'rating': 5}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)

    def test_delete_review(self):
        review = Review.objects.create(user=self.user, book=self.book, review_text="Great book", rating=5)
        url = reverse('review-delete', kwargs={'pk': review.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Review.objects.count(), 0)
        self.assertEqual(self.book.average_rating, None)  # Проверяем, что рейтинг обновился

    def test_rating_validation(self):
        url = reverse('review-list-create', kwargs={'book_id': self.book.id})
        data = {'review_text': 'Bad book', 'rating': 6}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('rating', response.data)