import requests

# URL de l'API pour créer un utilisateur
url = "http://localhost:8000/create-user/"

# Données de l'utilisateur à créer
user_data = {
    "username": "nouvelutilisateur",
    "password": "motdepassefort",
    "email": "utilisateur@example.com"
}

# Envoie de la requête POST
response = requests.post(url, data=user_data)

# Vérifier si l'utilisateur a été créé avec succès
if response.status_code == 201:
    print("Utilisateur créé avec succès !")
    print("Réponse de l'API :", response.json())
else:
    print("Erreur lors de la création de l'utilisateur.")
    print(response)
