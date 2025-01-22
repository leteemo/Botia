from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserSerializer
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from .serializers import MessageSerializer
from .models import Message

class ObtainTokenAPIView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        print(f"Authentification de l'utilisateur : {username}")
        user = authenticate(username=username, password=password)

        if user is not None:
            print(f"Utilisateur trouvé : {user.username}")
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)
        else:
            print(f"Authentification échouée pour : {username}")
            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)


class UserCreateAPIView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User created successfully", "user": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class getScripts(APIView):
    authentication_classes = [TokenAuthentication]  # Authentification par token

    def get(self, request):
        # Récupérer l'utilisateur authentifié à partir du token
        user = request.user

        # Récupérer les messages envoyés par cet utilisateur
        messages = Message.objects.filter(user=user)

        # Sérialiser les messages pour les retourner dans la réponse
        serializer = MessageSerializer(messages, many=True)

        # Retourner les informations de l'utilisateur et ses messages
        return Response({
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "messages": serializer.data
        })
    

class getAllScripts(APIView):
    authentication_classes = [TokenAuthentication]  # Authentification par token

    def get(self, request):
        # Récupérer tous les messages de tous les utilisateurs
        messages = Message.objects.all()

        # Sérialiser les messages pour les retourner dans la réponse
        serializer = MessageSerializer(messages, many=True)

        # Retourner tous les messages
        return Response({
            "message": "Accès autorisé",
            "messages": serializer.data  # Ajouter tous les messages dans la réponse
        })
    

    
    
class SendMessageAPIView(APIView):
    authentication_classes = [TokenAuthentication]  # Authentification par token

    def post(self, request):
        # Créer un message pour l'utilisateur authentifié
        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            # Lier l'utilisateur authentifié au message
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)