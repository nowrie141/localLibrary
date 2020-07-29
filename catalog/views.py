from django.shortcuts import render
from catalog.models import Book, Author, BookInstance, Genre, Language
from django.views import generic
# Create your views here.


def index(request):
    # View function for home page

    # Count number of books and instances
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    # Available books (Those with status = 'a')
    # We can filter a search with attribute__exact = 'value'
    num_instances_available = BookInstance.objects.filter(
        status__exact='a').count()

    #All in author is implied
    num_authors = Author.objects.count()

    num_genres = Genre.objects.all().count()

    num_languages = Language.objects.all().count()

    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_genres': num_genres,
        'num_languages': num_languages,
        'num_visits': num_visits,
    }

    # Render the HTML template index.html with the data in the context
    return render(request, 'index.html', context=context)


class BookListView(generic.ListView):
    # This view will actually be implemented as a class. We will be inheriting from an existing generic view function that already does most of what we want this view function to do, rather than writing our own from scratch.
    model = Book
    paginate_by = 5


class BookDetailView(generic.DetailView):
    model = Book


class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 5


class AuthorDetailView(generic.DetailView):
    model = Author
