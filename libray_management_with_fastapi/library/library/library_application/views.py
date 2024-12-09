from django.shortcuts import render
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import MyTokenObtainPairSerializer

class MyTokenObtainPairView(TokenObtainPairView):
    """
    Custom view to use the MyTokenObtainPairSerializer for JWT authentication.
    """
    serializer_class = MyTokenObtainPairSerializer
