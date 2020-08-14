from django.test import TestCase
from django.urls import reverse

from catalog.models import Author

import datetime

from django.utils import timezone
from django.contrib.auth.models import User

from catalog.models import BookInstance, Book, Genre, Language

import uuid

# Required to grant the permission needed to set a book as returned.
from django.contrib.auth.models import Permission


class AuthorListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create 13 authors for pagination tests
        number_of_authors = 13
        for author_id in range(number_of_authors):
            Author.objects.create(
                first_name=f'Ismael {author_id}',
                last_name=f'Surname {author_id}',
            )

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/catalog/authors/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('authors'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/author_list.html')

    def test_pagination_is_five(self):
        response = self.client.get(reverse('authors'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] == True)
        self.assertTrue(len(response.context['author_list']) == 5)


class LoanedBookInstancesByUserListViewTest(TestCase):
    def setUp(self):
        test_user1 = User.objects.create_user(
            username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(
            username='testuser2', password='2HJ1vRV0Z&3iD')

        test_user1.save()
        test_user2.save()

        test_author = Author.objects.create(
            first_name='Antonio', last_name='Banderas')

        test_genre = Genre.objects.create(name='Fantasy')

        test_language = Language.objects.create(name='Spanish')
        test_book = Book.objects.create(
            title='Title',
            summary='The summary',
            isbn='21321312312',
            author=test_author,
            language=test_language,
        )

        # Create genre as a post-step
        genre_objects_for_book = Genre.objects.all()
        # Direct assignment of many-to-many types not allowed
        test_book.genre.set(genre_objects_for_book)
        test_book.save()

        number_of_book_copies = 15

        for book_copy in range(number_of_book_copies):
            return_date = timezone.localtime()+datetime.timedelta(days=book_copy % 5)
            the_borrower = test_user1 if book_copy % 2 else test_user2
            status = 'm'
            BookInstance.objects.create(
                book=test_book,
                imprint='Not printend, 2016',
                due_back=return_date,
                borrower=the_borrower,
                status=status,
            )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('my-borrowed'))
        self.assertRedirects(
            response, '/accounts/login/?next=/catalog/mybooks/')

    def test_logged_in_uses_correct_template(self):
        login = self.client.login(
            username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('my-borrowed'))

        # Check that the user is actually logged in
        self.assertEqual(str(response.context['user']), 'testuser1')

        # Check that we got the correct response with success
        self.assertEqual(response.status_code, 200)

        # Check the correct templated is being used
        self.assertTemplateUsed(
            response, 'catalog/bookinstance_list_borrowed_user.html')

    def test_only_borrowed_books_in_list(self):
        login = self.client.login(
            username='testuser1',
            password='1X<ISRUkw+tuK'
        )

        response = self.client.get(reverse('my-borrowed'))

        # Check if user is logged in
        self.assertEqual(str(response.context['user']), 'testuser1')

        # Check that we got the correct response with success
        self.assertEqual(response.status_code, 200)

        # Check that initally we dont have any books in list (None on loan)
        self.assertTrue('bookinstance_list' in response.context)
        self.assertEqual(len(response.context['bookinstance_list']), 0)

        # Now change all books to be on loan
        books = BookInstance.objects.all()[:10]
        for book in books:
            book.status = 'o'
            book.save()

        # Check that now we have borrowed all books in the list
        response = self.client.get(reverse('my-borrowed'))

        # Check if user is logged in
        self.assertEqual(str(response.context['user']), 'testuser1')
        # Check that we got the correct response with success
        self.assertEqual(response.status_code, 200)

        self.assertTrue('bookinstance_list' in response.context)

        # Confirm all books are on loan by the user testuser1

        for bookitem in response.context['bookinstance_list']:
            self.assertEqual(
                response.context['user'],
                bookitem.borrower
            )
            self.assertEqual('o', bookitem.status)

    def test_pages_ordered_by_due_date(self):
        for book in BookInstance.objects.all():
            book.status = 'o'
            book.save()
        login = self.client.login(
            username='testuser1',
            password='1X<ISRUkw+tuK'
        )
        response = self.client.get(reverse('my-borrowed'))
        # Check if user is logged in
        self.assertEqual(
            str(response.context['user']),
            'testuser1'
        )

        # Check that we got the correct response with success
        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(response.context['bookinstance_list']), 5)

        last_date = 0
        for book in response.context['bookinstance_list']:
            if last_date == 0:
                last_date = book.due_back
            else:
                self.assertTrue(last_date <= book.due_back)
                last_date = book.due_back


class RenewBookInstancesViewTest(TestCase):
    def setUp(self):
        # Create users
        test_user1 = User.objects.create_user(
            username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(
            username='testuser2', password='2HJ1vRV0Z&3iD')

        test_user1.save()
        test_user2.save()

        # Give them permission
        permission = Permission.objects.get(name='Set book as returned')
        test_user2.user_permissions.add(permission)
        test_user2.save()

        # Create book
        test_author = Author.objects.create(
            first_name='Ismael', last_name='Garcia')
        test_genre = Genre.objects.create(name='Fantasy')
        test_language = Language.objects.create(name='English')
        test_book = Book.objects.create(
            title='Title',
            summary='Summary',
            isbn='2147621738',
            author=test_author,
            language=test_language
        )

        # Add genre as a post-step
        genre_objects_for_book = Genre.objects.all()
        # Direct assignment of many-to-many types not allowed.
        test_book.genre.set(genre_objects_for_book)
        test_book.save()

        # Create a bookinstance object for test_user1
        return_date = datetime.date.today() + datetime.timedelta(days=5)
        self.test_bookinstance1 = BookInstance.objects.create(
            book=test_book,
            imprint='Not print, 2020',
            due_back=return_date,
            borrower=test_user1,
            status='o',
        )

        # Create a bookinstance object for test_user2
        self.test_bookinstance2 = BookInstance.objects.create(
            book=test_book,
            imprint='Not print, 2020',
            due_back=return_date,
            borrower=test_user2,
            status='o',
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(
            reverse(
                'renew-book-librarian',
                kwargs={'pk': self.test_bookinstance1.pk}
            )
        )
        # Check redirect (the redirect URL is unpredictable)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_redirect_if_logged_in_but_not_correct_permission(self):
        login = self.client.login(
            username='testuser1',
            password='1X<ISRUkw+tuK'
        )
        response = self.client.get(
            reverse('renew-book-librarian',
                    kwargs={'pk': self.test_bookinstance1.pk}
                    )
        )
        self.assertEqual(response.status_code, 403)

    def test_logged_in_with_permission_borrowed_book(self):
        login = self.client.login(
            username='testuser2',
            password='2HJ1vRV0Z&3iD'
        )
        response = self.client.get(
            reverse(
                'renew-book-librarian',
                kwargs={'pk': self.test_bookinstance2.pk}
            )
        )
        # Check that it lets us login - this is our book and we have the right permissions.
        self.assertEqual(response.status_code, 200)

    def test_logged_in_with_permission_another_users_borrowed_book(self):
        login = self.client.login(
            username='testuser2',
            password='2HJ1vRV0Z&3iD'
        )
        response = self.client.get(
            reverse(
                'renew-book-librarian',
                kwargs={'pk': self.test_bookinstance1.pk}
            )
        )

       # Check that it lets us login. We're a librarian, so we can view any users book
        self.assertEqual(response.status_code, 200)

    def test_HTTP404_for_invalid_book_if_logged_in(self):
        # Wont match I hope
        test_uid = uuid.uuid4()
        login = self.client.login(
            username='testuser2',
            password='2HJ1vRV0Z&3iD'
        )
        response = self.client.get(
            reverse(
                'renew-book-librarian',
                kwargs={'pk': test_uid}
            )
        )
        self.assertEqual(response.status_code, 404)

    def test_uses_correct_template(self):
        login = self.client.login(
            username='testuser2',
            password='2HJ1vRV0Z&3iD'
        )
        response = self.client.get(
            reverse(
                'renew-book-librarian',
                kwargs={'pk': self.test_bookinstance1.pk}
            )
        )
        self.assertEqual(response.status_code, 200)
        # Check we used correct template
        self.assertTemplateUsed(response, 'catalog/book_renew_librarian.html')

    # Checks that the initial date for the form is three weeks in the future
    def test_form_renewal_date_initially_has_date_three_weeks_in_future(self):
        login = self.client.login(
            username='testuser2',
            password='2HJ1vRV0Z&3iD'
        )
        response = self.client.get(
            reverse(
                'renew-book-librarian',
                kwargs={'pk': self.test_bookinstance1.pk}
            )
        )
        self.assertEqual(response.status_code, 200)
        date_3_weeks_in_future = datetime.date.today() + datetime.timedelta(weeks=3)
        self.assertEqual(
            response.context['form'].initial['renewal_date'], date_3_weeks_in_future
        )

    def test_redirects_to_all_borrowed_book_list_on_success(self):
        login = self.client.login(
            username='testuser2',
            password='2HJ1vRV0Z&3iD'
        )
        valid_date_in_future = datetime.date.today() + datetime.timedelta(weeks=2)
        response = self.client.post(
            reverse(
                'renew-book-librarian',
                kwargs={'pk': self.test_bookinstance1.pk}
            ),
            {'renewal_date': valid_date_in_future}
        )
        self.assertRedirects(response, reverse('all-borrowed'))

    def test_form_invalid_renewal_date_past(self):
        login = self.client.login(
            username='testuser2',
            password='2HJ1vRV0Z&3iD'
        )
        date_in_past = datetime.date.today() - datetime.timedelta(weeks=1)
        response = self.client.post(
            reverse(
                'renew-book-librarian',
                kwargs={'pk': self.test_bookinstance1.pk}
            ),
            {'renewal_date': date_in_past}
        )
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response,
            'form',
            'renewal_date',
            'Invalid date - renewal in past'
        )

    def test_form_invalid_renewal_date_future(self):
        login = self.client.login(
            username='testuser2',
            password='2HJ1vRV0Z&3iD'
        )

        invalid_date_in_future = datetime.date.today() + datetime.timedelta(weeks=5)

        response = self.client.post(
            reverse(
                'renew-book-librarian',
                kwargs={'pk': self.test_bookinstance1.pk}
            ),
            {'renewal_date': invalid_date_in_future}
        )

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response,
            'form',
            'renewal_date',
            'Invalid date - renewal more than 4 weeks ahead'
        )


class CreateAuthorViewTest(TestCase):
    def setUp(self):
        test_user1 = User.objects.create_user(
            username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(
            username='testuser2', password='2HJ1vRV0Z&3iD')
        test_user1.save()
        test_user2.save()

        # Give them permission
        permission = Permission.objects.get(name='Set book as returned')
        test_user2.user_permissions.add(permission)
        test_user2.save()

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(
            reverse('author_create')
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_redirect_if_logged_in_but_not_correct_permission(self):
        login = self.client.login(
            username='testuser1',
            password='1X<ISRUkw+tuK'
        )
        response = self.client.get(
            reverse('author_create')
        )
        self.assertEqual(response.status_code, 403)

    def test_logged_in_with_permission_author_create(self):
        login = self.client.login(
            username='testuser2',
            password='2HJ1vRV0Z&3iD'
        )
        response = self.client.get(
            reverse('author_create')
        )
        # Check that it lets us login and create a new author.
        self.assertEqual(response.status_code, 200)

    def test_form_date_initially_is_today(self):
        login = self.client.login(
            username='testuser2',
            password='2HJ1vRV0Z&3iD'
        )
        response = self.client.get(
            reverse('author_create')
        )
        self.assertEqual(response.status_code, 200)
        date_today = datetime.date.today()
        self.assertEqual(
            response.context['form'].initial['date_of_death'], date_today
        )

    def test_redirects_to_created_author_on_success(self):
        login = self.client.login(
            username='testuser2',
            password='2HJ1vRV0Z&3iD'
        )
        date_in_past = datetime.date.today() - datetime.timedelta(weeks=2)
        date_in_future = datetime.date.today() + datetime.timedelta(weeks=2)
        response = self.client.post(
            reverse('author_create'),
            {
                'first_name': 'testName',
                'last_name': 'testLastName',
                'date_of_birth': date_in_past,
                'date_of_death': date_in_future,
            }
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/catalog/author/'))

    def test_logged_in_uses_correct_template(self):
        login = self.client.login(
            username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('author_create'))

        # Check that the user is actually logged in
        self.assertEqual(str(response.context['user']), 'testuser2')

        # Check that we got the correct response with success
        self.assertEqual(response.status_code, 200)

        # Check the correct templated is being used
        self.assertTemplateUsed(
            response, 'catalog/author_form.html')
