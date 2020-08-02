from django.contrib import admin

from .models import Author, Genre, Book, BookInstance, Language

# Register your models here.
# admin.site.register(Author)
admin.site.register(Genre)
# admin.site.register(Book)
# admin.site.register(BookInstance)
admin.site.register(Language)

# Show the books writen by an author


class BooksInline(admin.TabularInline):
    model = Book


class AuthorAdmin(admin.ModelAdmin):
    # Configure how the lists will be displayed
    list_display = ('last_name', 'first_name',
                    'date_of_birth', 'date_of_death')
    # The fields attribute lists just those fields that are to be displayed on the form, in order.
    fields = ['first_name', 'last_name', ('date_of_birth', 'date_of_death')]
    inlines = [BooksInline]


admin.site.register(Author, AuthorAdmin)

# Makes sense to have both the book information and information about the specific copies you've got on the same detail page


class BooksInstanceInline(admin.TabularInline):
    model = BookInstance

#  The @register decorator to register the models (this does exactly the same thing as the admin.site.register() syntax)
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    # Configure how the lists will be displayed
    list_display = ('title', 'author', 'display_genre')
    # Display the instances as TabularInline
    inlines = [BooksInstanceInline]


@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
    # Filter the books for the status or the date
    list_filter = ('status', 'due_back')
    # Configure how the lists will be displayed
    list_display = ('book', 'status', 'borrower', 'due_back', 'id')
    # Each section has its own title (or None, if you don't want a title) and an associated tuple of fields in a dictionary
    fieldsets = (
        (None, {
            'fields': ('book', 'imprint', 'id')
        }),
        ('Availability', {
            'fields': ('status', 'due_back', 'borrower')
        }),
    )
