from django.contrib import admin
from .models import Libraryadmin, LibraryUser, BorrowRequest

# Register your models here.
admin.site.register(Libraryadmin)
admin.site.register(LibraryUser)
admin.site.register(BorrowRequest)