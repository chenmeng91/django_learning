import datetime

from django.contrib.auth.models import Permission, User
from django.test import TestCase
from django.urls import reverse

from .forms import RenewBookForm
from .models import Author, Book, BookInstance, Genre, Language


class CatalogTestDataMixin:
    @classmethod
    def setUpTestData(cls):
        cls.author = Author.objects.create(
            first_name='John',
            last_name='Smith',
            date_of_birth='1950-01-01',
        )
        cls.genre = Genre.objects.create(name='Fantasy')
        cls.language = Language.objects.create(name='English')
        cls.book = Book.objects.create(
            title='The Test Book',
            author=cls.author,
            summary='A book used by the test suite.',
            isbn='1234567890123',
            language=cls.language,
        )
        cls.book.genre.add(cls.genre)
        cls.borrower = User.objects.create_user(
            username='borrower',
            password='test-password',
        )
        cls.librarian = User.objects.create_user(
            username='librarian',
            password='test-password',
        )
        permission = Permission.objects.get(codename='can_mark_returned')
        cls.librarian.user_permissions.add(permission)
        cls.loan = BookInstance.objects.create(
            book=cls.book,
            imprint='Test imprint',
            due_back=datetime.date.today() + datetime.timedelta(days=7),
            borrower=cls.borrower,
            status='o',
        )
        cls.available_copy = BookInstance.objects.create(
            book=cls.book,
            imprint='Available imprint',
            status='a',
        )


class AuthorModelTest(CatalogTestDataMixin, TestCase):
    def test_author_string_is_last_name_comma_first_name(self):
        self.assertEqual(str(self.author), 'Smith, John')

    def test_author_get_absolute_url(self):
        self.assertEqual(self.author.get_absolute_url(), f'/catalog/author/{self.author.id}/')


class BookModelTest(CatalogTestDataMixin, TestCase):
    def test_book_string_is_title(self):
        self.assertEqual(str(self.book), 'The Test Book')

    def test_book_get_absolute_url(self):
        self.assertEqual(self.book.get_absolute_url(), f'/catalog/book/{self.book.id}/')

    def test_display_genre(self):
        self.assertEqual(self.book.display_genre(), 'Fantasy')


class BookInstanceModelTest(CatalogTestDataMixin, TestCase):
    def test_is_overdue_false_for_future_due_date(self):
        self.assertFalse(self.loan.is_overdue)

    def test_is_overdue_true_for_past_due_date(self):
        self.loan.due_back = datetime.date.today() - datetime.timedelta(days=1)
        self.assertTrue(self.loan.is_overdue)


class RenewBookFormTest(TestCase):
    def test_renewal_date_in_past_is_invalid(self):
        date = datetime.date.today() - datetime.timedelta(days=1)
        form = RenewBookForm(data={'renewal_date': date})
        self.assertFalse(form.is_valid())

    def test_renewal_date_more_than_four_weeks_ahead_is_invalid(self):
        date = datetime.date.today() + datetime.timedelta(weeks=4, days=1)
        form = RenewBookForm(data={'renewal_date': date})
        self.assertFalse(form.is_valid())

    def test_renewal_date_within_four_weeks_is_valid(self):
        date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(data={'renewal_date': date})
        self.assertTrue(form.is_valid())


class IndexViewTest(CatalogTestDataMixin, TestCase):
    def test_index_view_uses_template_and_counts_records(self):
        response = self.client.get(reverse('index'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')
        self.assertContains(response, 'Books:</strong> 1')
        self.assertContains(response, 'Copies:</strong> 2')
        self.assertContains(response, 'Copies available:</strong> 1')
        self.assertContains(response, 'Authors:</strong> 1')

    def test_index_view_tracks_session_visits(self):
        self.client.get(reverse('index'))
        response = self.client.get(reverse('index'))

        self.assertEqual(response.context['num_visits'], 2)


class BookListViewTest(CatalogTestDataMixin, TestCase):
    def test_book_list_view_accessible_by_name(self):
        response = self.client.get(reverse('books'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/book_list.html')
        self.assertContains(response, 'The Test Book')


class BookDetailViewTest(CatalogTestDataMixin, TestCase):
    def test_book_detail_view_displays_book_data(self):
        response = self.client.get(reverse('book-detail', args=[self.book.id]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'The Test Book')
        self.assertContains(response, '1234567890123')


class AuthorListViewTest(CatalogTestDataMixin, TestCase):
    def test_author_list_view_accessible_by_name(self):
        response = self.client.get(reverse('authors'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/author_list.html')
        self.assertContains(response, 'Smith, John')


class BorrowedBooksViewTest(CatalogTestDataMixin, TestCase):
    def test_redirects_to_login_when_not_logged_in(self):
        response = self.client.get(reverse('my-borrowed'))

        self.assertRedirects(response, f"{reverse('login')}?next={reverse('my-borrowed')}")

    def test_logged_in_user_sees_own_borrowed_books(self):
        self.client.force_login(self.borrower)
        response = self.client.get(reverse('my-borrowed'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'The Test Book')
        self.assertEqual(list(response.context['bookinstance_list']), [self.loan])


class RenewBookViewTest(CatalogTestDataMixin, TestCase):
    def test_renew_book_requires_permission(self):
        self.client.force_login(self.borrower)
        response = self.client.get(reverse('renew-book-librarian', args=[self.loan.id]))

        self.assertEqual(response.status_code, 302)

    def test_librarian_can_renew_book(self):
        self.client.force_login(self.librarian)
        new_due_date = datetime.date.today() + datetime.timedelta(weeks=2)
        response = self.client.post(
            reverse('renew-book-librarian', args=[self.loan.id]),
            {'renewal_date': new_due_date},
        )

        self.assertRedirects(response, reverse('all-borrowed'))
        self.loan.refresh_from_db()
        self.assertEqual(self.loan.due_back, new_due_date)
