from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from datetime import date
import uuid


class Genre(models.Model):
    # Model representing a book genre
    # name is charfield because contains letters and numbers
    name = models.CharField(max_length=200, help_text='Enter a book genre...')

    # Minimally, in every model you should define the standard Python class method __str__() to return a human-readable string for each object.
    def __str__(self):
        # String for representing the Model object
        return self.name


class Language(models.Model):
    # Model representing a Language
    name = models.CharField(max_length=200,
                            help_text="Enter the book's language")

    def __str__(self):
        # String for representing the Model object (in Admin site etc.)
        return self.name


class Book(models.Model):
    # Model representing a book (Not an instance)
    title = models.CharField(max_length=200)

    # Add the foreignkey because one book can only have one author but one author can have multiple books
    # Author as a string rather than object because it hasn't been declared yet in the file
    author = models.ForeignKey('Author', on_delete=models.SET_NULL, null=True)

    # Summary of the book
    summary = models.TextField(
        max_length=1000, help_text='Enter a brief description of the book')
    isbn = models.CharField(
        'ISBN', max_length=13, help_text='13 Character <a href="https://www.isbn-international.org/content/what-isbn">ISBN number</a>')

    language = models.ForeignKey(
        'Language', on_delete=models.SET_NULL, null=True)

    # One book has minimum 1 genre or many, one genre could have 0 or many books
    genre = models.ManyToManyField(
        Genre, help_text='Select a genre for this book')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('book-detail', args=[str(self.id)])
    # Displays every genre as a string concatenated because Django doest allow to show ManyToManyField

    def display_genre(self):
        return ', '.join(genre.name for genre in self.genre.all()[:3])

    display_genre.short_description = 'Genre'


class BookInstance(models.Model):
    # Model representing a specific copy of a book
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          help_text='Unique ID for this particular instance of the book')
    book = models.ForeignKey('Book', on_delete=models.SET_NULL, null=True)
    imprint = models.CharField(max_length=200)
    due_back = models.DateField(null=True, blank=True)

    LOAN_STATUS = (
        ('m', 'Maintenance'),
        ('o', 'On loan'),
        ('a', 'Available'),
        ('r', 'Reserved'),
    )

    status = models.CharField(max_length=1, choices=LOAN_STATUS,
                              blank=True, default='m', help_text='Book availability')

    borrower = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)

    @property
    def is_overdue(self):
        if self.due_back and date.today() > self.due_back:
            return True
        return False

    class Meta:
        ordering = ['due_back']
        # Defining permissions is done on the model "class Meta" section, using the permissions field.
        permissions = (
            ("can_mark_returned", "Set book as returned"),
        )

    def __str__(self):
        return f'{self.id} ({self.book.title})'


class Author(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField('died', null=True, blank=True)

    def get_absolute_url(self):
        return reverse('author-detail', args=[str(self.id)])

    class Meta:
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f'{self.last_name}, {self.first_name}'
