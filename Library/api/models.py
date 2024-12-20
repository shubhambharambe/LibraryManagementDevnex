import random
from datetime import timedelta,date
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator

class User(AbstractUser):
    role_choices = [
        ('librarian', 'Librarian'),
        ('borrower', 'Borrower')
    ]
    username = models.CharField(max_length=50, blank=True, null=True, unique=True)
    email = models.EmailField(('email address'), unique=True)
    first_name = models.CharField(max_length=50, blank=False)
    last_name = models.CharField(max_length=50, blank=False)
    mobile_no = models.IntegerField(null=True)
    user_role = models.CharField(max_length=10, choices=role_choices, default='borrower')
    user_address = models.CharField(max_length=50, blank=False, null=True)
    city = models.CharField(max_length=40)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return "{}".format(self.email)


class Author(models.Model):
    name = models.CharField(max_length=255)
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.CharField(null=True, max_length=100, blank=True)

    def __str__(self):
        return f"{self.name}"


import random
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.ForeignKey('Author', on_delete=models.CASCADE, related_name='books')
    isbn = models.IntegerField(unique=True, null=False, blank=False,
                                validators=[
                                    MinValueValidator(10000000),  # Minimum value for 8 digits
                                    MaxValueValidator(99999999)  # Maximum value for 8 digits
                                ])
    total_copies = models.PositiveIntegerField(default=0)
    available_copies = models.PositiveIntegerField(default=0)
    category = models.ForeignKey('Category', related_name='books', on_delete=models.CASCADE)
    price = models.PositiveIntegerField(null=False)
    created_by = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_books')
    copy_isbns = models.JSONField(default=list, blank=True)  # Store individual copy ISBNs
    published_date = models.DateField()

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Ensure available_copies does not exceed total_copies
        if self.available_copies > self.total_copies:
            self.available_copies = self.total_copies
        
        # Generate ISBNs for the copies if not already generated
        if not self.copy_isbns:
            self.generate_copy_isbns()

        super().save(*args, **kwargs) 
    


    def generate_copy_isbns(self):
        """Generates unique ISBNs for each copy of the book."""
        self.copy_isbns = []
        for i in range(1, self.total_copies + 1):
            # Generate the unique copy ISBN by appending a number to the base ISBN
            copy_isbn = f"{self.isbn}{str(i).zfill(6)}"  # Adding 4 digits to make it unique for each copy
            self.copy_isbns.append(copy_isbn)



class BorrowRecord(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ]
    
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='borrow_records')
    borrowed_by = models.ForeignKey(User, related_name='borrowed_books', on_delete=models.CASCADE)
    borrow_date = models.DateField(auto_now_add=True)
    return_date = models.DateField(blank=True, null=True)
    fine = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    expected_return_date = models.DateField(blank=True, null=True)
    copy_isbn = models.CharField(max_length=14, blank=True, null=True)  # Add a field for copy ISBN

    def __str__(self):
        return f"{self.borrowed_by.username} borrowed {self.book.title} with ISBN {self.book.isbn}"

    def save(self, *args, **kwargs):
        # Ensure borrow_date is set
        if not self.borrow_date:
            self.borrow_date = date.today()

        # Set expected_return_date if not already set
        if not self.expected_return_date:
            self.expected_return_date = self.borrow_date + timedelta(days=10)

        
        if self.return_date and self.return_date > self.expected_return_date:
            overdue_days = (self.return_date - self.expected_return_date).days
            if overdue_days <= 8:
                self.fine = overdue_days * 10
            else:
                self.fine = (8 * 10) + ((overdue_days - 8) * 20)
        else:
            self.fine = 0

        
        if not self.return_date:
            if self.book.available_copies > 0:
                self.book.available_copies -= 1
                self.book.save()

                
                self.copy_isbn = self.book.copy_isbns[0] 
                self.book.copy_isbns.pop(0)
                self.book.save()

        else:
            self.book.available_copies += 1
            self.book.copy_isbns.append(self.copy_isbn)
            
            self.book.save()
        super().save(*args, **kwargs)
        