import requests
import os

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
    try:
        response = requests.post(url, data=data)
        return response
    except requests.RequestException as e:
        print(f"Erreur réseau : {e}")
        return None

# Fonction pour obtenir un token via l'API
def get_token(username, password):
    url = BASE_URL + "get-token/"
    data = {
        "username": username,
        "password": password
    }
    try:
        response = requests.post(url, data=data)
        print("Response status code:", response.status_code)
        print("Response body:", response.text)
        return response
    except requests.RequestException as e:
        print(f"Erreur réseau : {e}")
        return None

def get_scripts(token, api_name):
    url = BASE_URL + api_name
    headers = {
        "Authorization": f"Token {token}"
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        print("Accès autorisé à l'API protégée!")
        return response.json()
    else:
        return None

def send_script(token, content, name="default name"):
    url = BASE_URL + "send-message/"
    headers = {
        "Authorization": f"Token {token}"
    }
    data = {
        "name": name,
        "content": content
    }
    print("envoyé:", content)
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 201:
        print("Message envoyé avec succès!")
        print(response.json())
    else:
        print(f"Erreur lors de l'envoi du message: {response.status_code}")
        print(response.json())


def add_or_update_env_variable(file_path, variable_name, value):
    """
    Ajoute ou met à jour une variable dans un fichier .env, en s'assurant qu'elle est ajoutée à la dernière ligne.
    :param file_path: Chemin du fichier .env
    :param variable_name: Nom de la variable
    :param value: Valeur de la variable
    """
    # Lire le contenu actuel du fichier .env si il existe
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            lines = file.readlines()
    else:
        lines = []

    # Vérifier si la variable existe déjà
    variable_found = False
    for i, line in enumerate(lines):
        if line.startswith(f"{variable_name}="):
            # Si elle existe, on met à jour la ligne correspondante
            lines[i] = f"{variable_name}={value}\n"
            variable_found = True
            break

    # Si la variable n'existe pas, on l'ajoute à la fin
    if not variable_found:
        lines.append(f"{variable_name}={value}\n")

    # Réécrire les lignes dans le fichier .env, avec la nouvelle variable ajoutée à la dernière ligne
    with open(file_path, 'w') as file:
        file.writelines(lines)

def get_api_token_from_env(file_path):
    """
    Fonction pour lire la variable API_TOKEN dans le fichier .env.
    :param file_path: Chemin du fichier .env
    :return: Le token si trouvé, sinon None
    """
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            for line in file:
                # Si la ligne commence par 'API_TOKEN=', on retourne le token
                if line.startswith("API_TOKEN="):
                    return line.strip().split('=')[1]
    return None