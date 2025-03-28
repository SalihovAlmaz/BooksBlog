from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from booksblog.models import Book, Genres, Tags, Review, ReadingStatus

User = get_user_model()


class BookAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client.login(username='testuser', password='password123')
        self.genre = Genres.objects.create(name='Fantasy', slug='fantasy')
        self.tag = Tags.objects.create(name='Magic', slug='magic')
        self.book = Book.objects.create(title='Test Book', slug='test-book', author=self.user)
        self.book.tags.add(self.tag)

    def test_get_books_list(self):
        response = self.client.get('/api/books/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Test Book", response.data["results"][0]["title"])

    def test_get_book_detail(self):
        response = self.client.get(f'/api/books/{self.book.slug}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Book')

    def test_create_book_unauthorized(self):
        self.client.logout()
        response = self.client.post('/api/books/', {'title': 'New Book', 'slug': 'new-book'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_book_authorized(self):
        response = self.client.post(
            '/api/books/',
            {'title': 'New Book', 'slug': 'new-book', 'author': self.user.id, 'genres': [self.genre.id]}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 2)

    def test_delete_book(self):
        response = self.client.delete(f'/api/books/{self.book.slug}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Book.objects.count(), 0)


class UserAuthTestCase(APITestCase):
    def test_user_registration(self):
        response = self.client.post('/api/register/', {'username': 'newuser', 'password': 'password123'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_user_login(self):
        User.objects.create_user(username='testuser', password='password123')
        response = self.client.post('/api/token/', {'username': 'testuser', 'password': 'password123'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)


class ReviewAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client.login(username='testuser', password='password123')
        self.book = Book.objects.create(title='Test1 Book', slug='test-book', author=self.user)
        Review.objects.all().delete()

    def test_create_review(self):
        response = self.client.post(
            f'/api/books/{self.book.slug}/reviews/',
            {'review_text': 'Amazing!', 'rating': 5}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_reviews(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/api/books/{self.book.slug}/reviews/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Great book!', response.data[0]['review_text'])


class ReadingStatusAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.book = Book.objects.create(title='Test Book', slug='test-book', author=self.user)
        self.reading_status = ReadingStatus.objects.create(user=self.user, book=self.book, status='reading')
        self.client.login(username='testuser', password='password123')

    def test_create_reading_status(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.post('/api/reading-status/', {'book': self.book.id, 'status': 'finished'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_reading_status(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.get('/api/reading-status/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('reading', response.data[0]['status'])
