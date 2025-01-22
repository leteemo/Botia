import requests

# Adresse de base de l'API (en fonction de ton serveur local)
BASE_URL = "http://127.0.0.1:8000/api/"

# Fonction pour créer un utilisateur via l'API
def create_user(username, password, first_name, last_name, email):
    url = BASE_URL + "create-user/"
    data = {
        "username": username,
        "password": password,
        "first_name": first_name,
        "last_name": last_name,
        "email": email
    }
    response = requests.post(url, data=data)
    if response.status_code == 201:
        print("Utilisateur créé avec succès!")
    else:
        print(f"Erreur lors de la création de l'utilisateur: {response.status_code}")
        print(response.json())

# Fonction pour obtenir un token via l'API
def get_token(username, password):
    url = BASE_URL + "get-token/"
    data = {
        "username": username,
        "password": password
    }
    response = requests.post(url, data=data)
    if response.status_code == 200:
        token = response.json().get("token")
        print(f"Token récupéré: {token}")
        return token
    else:
        print(f"Erreur lors de l'obtention du token: {response.status_code}")
        print(response.json())
        return None

# Fonction pour tester une requête protégée avec le token
def test_protected_api(token):
    url = BASE_URL + "get-all-scripts/"
    headers = {
        "Authorization": f"Token {token}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        print("Accès autorisé à l'API protégée!")
        print(response.json())
    else:
        print(f"Erreur d'accès: {response.status_code}")
        print(response.json())

def send_message(token, content):
    url = BASE_URL + "send-message/"
    headers = {
        "Authorization": f"Token {token}"
    }
    data = {
        "content": content
    }
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 201:
        print("Message envoyé avec succès!")
        print(response.json())
    else:
        print(f"Erreur lors de l'envoi du message: {response.status_code}")
        print(response.json())


if __name__ == "__main__":
    # Crée un utilisateur (à ajuster selon tes besoins)
    create_user(
        username="testuser2",
        password="strongpassword",
        first_name="Test2",
        last_name="User2",
        email="testuser2@example.com"
    )

    # Récupère un token pour cet utilisateur
    token = get_token("testuser2", "strongpassword")

    send_message(token, "bonjour")

    # Si le token est récupéré, tester l'accès à une API protégée
    if token:
        test_protected_api(token)
