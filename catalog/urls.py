from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('books/', views.BookListView.as_view(), name='books'),
    # <int:pk> allows us to capture the book id
    # We can use re_path if we want to use regex
    path('book/<int:pk>', views.BookDetailView.as_view(), name='book-detail'),

    path('authors/', views.AuthorListView.as_view(), name='authors'),
    path('authors/<int:pk>', views.AuthorDetailView.as_view(), name='author-detail'),

    path('mybooks/', views.LoanedBookByUserListView.as_view(), name="my-borrowed"),

    path('borrowedbooks/', views.AllLoanedBookListView.as_view(), name="all-borrowed"),
    path('book/<uuid:pk>/renew/', views.renew_book_librarian,
         name='renew-book-librarian'),

    path('author/create/',
         views.AuthorCreate.as_view(), name="author_create"),

    path('author/<int:pk>/update/',
         views.AuthorUpdate.as_view(), name="author_update"),

    path('author/<int:pk>/delete/',
         views.AuthorDelete.as_view(), name="author_delete"),

    path('book/create/',
         views.BookCreate.as_view(), name="book_create"),

    path('book/<int:pk>/update/',
         views.BookUpdate.as_view(), name="book_update"),

    path('book/<int:pk>/delete/',
         views.BookDelete.as_view(), name="book_delete"),
]
