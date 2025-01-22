from django.db import models
from django.db import models
from django.contrib.auth.models import User

class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # L'utilisateur qui envoie le message
    name = models.TextField()
    content = models.TextField()  # Le contenu du message
    created_at = models.DateTimeField(auto_now_add=True)  # La date de création du message

    def __str__(self):
        return f"Message de {self.user.username} - {self.created_at}"