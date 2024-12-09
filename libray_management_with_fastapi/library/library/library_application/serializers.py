from rest_framework import serializers
from .models import LibraryUser, Libraryadmin, BorrowRequest
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
# from rest_framework_simplejwt.views import TokenObtainPairView


class BookSerializer(serializers.ModelSerializer):
    """
    Serializer for book listing
    """
    available_copies = serializers.SerializerMethodField()
    
    class Meta:
        model = Libraryadmin
        fields = '__all__'

class BookSerializer(serializers.ModelSerializer):
    """
    Serializer for book listing
    """
    available_copies = serializers.SerializerMethodField()
    
    class Meta:
        model = LibraryUser
        fields = '__all__'
    
class BookSerializer(serializers.ModelSerializer):
    """
    Serializer for book listing
    """
    available_copies = serializers.SerializerMethodField()
    
    class Meta:
        model = BorrowRequest
        fields = '__all__'



class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['username'] = user.username
        if user.is_staff:  # Check if the user is an admin
            token['role'] = 'admin'
        else:
            token['role'] = 'user'
