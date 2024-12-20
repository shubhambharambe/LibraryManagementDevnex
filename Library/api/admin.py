from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import User, Author, Category, Book, BorrowRecord


# Customizing the User Admin
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'user_role', 'city', 'mobile_no')
    list_filter = ('user_role', 'city')
    search_fields = ('email', 'first_name', 'last_name', 'mobile_no')


# Customizing the Author Admin
@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


# Customizing the Category Admin
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
    list_filter = ('name',)


# Customizing the Book Admin
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'isbn', 'total_copies', 'available_copies', 'price', 'category', 'created_by', 'published_date')
    list_filter = ('author', 'category', 'published_date')
    search_fields = ('title', 'isbn', 'author__name', 'category__name')
    readonly_fields = ('copy_isbns',)  # Make copy_isbns read-only in admin
    fieldsets = (
        (None, {
            'fields': ('title', 'author', 'category', 'isbn', 'price', 'published_date')
        }),
        ('Stock Information', {
            'fields': ('total_copies', 'available_copies', 'copy_isbns')
        }),
        ('Creator Info', {
            'fields': ('created_by',)
        }),
    )


# Customizing the Borrow Record Admin
@admin.register(BorrowRecord)
class BorrowRecordAdmin(admin.ModelAdmin):
    list_display = ('book', 'borrowed_by', 'borrow_date', 'return_date', 'status', 'fine')
    list_filter = ('status', 'borrow_date', 'return_date')
    search_fields = ('book__title', 'borrowed_by__email', 'status')
