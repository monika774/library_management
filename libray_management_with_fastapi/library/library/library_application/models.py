from django.db import models
import uuid
# Create your models here.


class Libraryadmin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    book_name = models.CharField(max_length=255)
    book_author = models.CharField(max_length=255)
    book_publish_date = models.DateField(auto_now_add=False)
    quantity_of_book = models.IntegerField()


class LibraryUser(models.Model):
    """
    Custom user model for library management system
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=255)
    std  = models.IntegerField()
    roll_no = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
class BorrowRequest(models.Model):
    STATUS_BOOK = [
        ("issued", "Issued"),
        ("pending", "Pending"),
        ("processing", "On process"),
    ]
    
    user_id = models.ForeignKey(LibraryUser, on_delete=models.CASCADE)
    book_id = models.ForeignKey(Libraryadmin, on_delete=models.CASCADE)
    issue_date = models.DateField(auto_now_add=True)
    submit_date = models.DateField()
    status = models.CharField(max_length=255, choices=STATUS_BOOK)
