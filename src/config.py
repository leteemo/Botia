import os

LLM_IMAGES_NAME_SENDING_AUTORISATION = True
LLM_CASCADE_NAME_SENDING_AUTORISATION = True

# Exemple de code de ta fonction CHOICE_PROMPT
def CHOICE_PROMPT(image_name):
    images = IMAGES_NAMES(LLM_IMAGES_NAME_SENDING_AUTORISATION)
    cascades = CASCADES_NAMES(LLM_CASCADE_NAME_SENDING_AUTORISATION)

    prompt = f"""
        En analyse d'image il existe plusieurs techniques pour reconnaitre une image.
        Quelle est la meilleure méthode pour reconnaitre un/e {image_name} avec les informations suivantes:\n
        fichiers images: {images}\n
        fichiers cascades: {cascades}
        réponses possibles: natural point, template matching, haar cascade

        répondre seulement en json sous ce format sans commentaires:
        {{"meilleur": "<nom>"}}
    """
    return prompt


def IMAGES_NAMES(Authorization):
    files = []
    if Authorization:
        dossier = 'img/'
        for fichier in os.listdir(dossier):
            chemin_complet = os.path.join(dossier, fichier)
            if os.path.isfile(chemin_complet):
                files.append(fichier)
    return files if files else None

def CASCADES_NAMES(Authorization):
    files = []
    if Authorization:
        dossier = 'cascade/' 
        for fichier in os.listdir(dossier):
            chemin_complet = os.path.join(dossier, fichier)
            if os.path.isfile(chemin_complet):
                files.append(fichier)
    return files if files else None


images = IMAGES_NAMES(LLM_IMAGES_NAME_SENDING_AUTORISATION)
cascades = CASCADES_NAMES(LLM_CASCADE_NAME_SENDING_AUTORISATION)


INIT_PROMPT = """L'objectif est de  te baser sur cet exemple de structure json afin de me renvoyer des instructions:

{
    // node nommé Start
    "Start": {
        "inputs": {},
        "outputs": {
            "output": [
                {
                    "connected node": "For Loop",
                    "connected input": "input"
                }
            ]
        },
        "widgets": {},
        "coord": {
            "x": 88.4627191104806,
            "y": 321.8728815362972
        },
        "type": "StartNode",
        "identifier": "start"
    },
    // node nommé Delay
    "Delay": {
        "inputs": {
            "input": "input"
        },
        "outputs": {
            "output": [
                {
                    "connected node": "Get Image Coord",
                    "connected input": "input"
                }
            ]
        },
        "widgets": {
            "delay": "5"
        },
        "coord": {
            "x": 843.4438394724064,
            "y": 323.80740541822365
        },
        "type": "DelayNode",
        "identifier": "control"
    },
    "Move Mouse": {
        "inputs": {
            "input": "input",
            "data": "data"
        },
        "outputs": {
            "output": [
                {
                    "connected node": "Key",
                    "connected input": "input"
                }
            ]
        },
        "widgets": {
            "coor x": "1",
            "coor y": "1"
        },
        "coord": {
            "x": 1620.7747299511564,
            "y": 311.7108637044874
        },
        "type": "MoveMouseNode",
        "identifier": "action"
    },
    "Get Image Coord": {
        "inputs": {
            "input": "input"
        },
        "outputs": {
            "output": [
                {
                    "connected node": "Move Mouse",
                    "connected input": "input"
                }
            ],
            "data": [
                {
                    "connected node": "Move Mouse",
                    "connected input": "data"
                }
            ]
        },
        "widgets": {
            "image src": "amixem.png",
            "precision": "0.7"
        },
        "coord": {
            "x": 1202.6303455746252,
            "y": 312.588442996579
        },
        "type": "GetImageCoordNode",
        "identifier": "action"
    },
    "For Loop": {
        "inputs": {
            "input": "input"
        },
        "outputs": {
            "output": [
                {
                    "connected node": "Delay",
                    "connected input": "input"
                }
            ],
            "end_output": []
        },
        "widgets": {
            "begin": "0",
            "end": "5"
        },
        "coord": {
            "x": 425.9235146641562,
            "y": 325.39765211514657
        },
        "type": "ForLoopNode",
        "identifier": "control"
    },
    "Key": {
        "inputs": {
            "input": "input"
        },
        "outputs": {
            "output": []
        },
        "widgets": {
            "key": "tab"
        },
        "coord": {
            "x": 2036.4293214864451,
            "y": 312.20701244334947
        },
        "type": "KeyNode",
        "identifier": "action"
    }
}

C'est basé sur des classes python dont:

class ClickMouseNode(Node):
    __identifier__ = 'action'  # Identifiant du noeud
    NODE_NAME = 'ClickMouseNode'       # Nom du noeud

    def __init__(self):
        super(ClickMouseNode, self).__init__()

        # Ajout de ports d'entrée et de sortie
        self.add_input('input')
        self.add_output('output')
        
        items = ['right', 'left']
        self.add_combo_menu('click', 'click', items)

liste des neouds: action.KeyNode, action.GetImageCoordNode, control.DelayNode, action.GetImageCoordNode, action.MoveMouseNode, control.DelayNode

Il faut être très exacte sur le type et l'identifier.
C'est un graphe où tu peux mettre le nom que tu veux pour les node, les "type" permettent de donner l'action effectué par le node.
coord permet de placer le node dans l'interface graphique.
Le premier node devra être un Start.
Un input ne peut être connecté qu'à un output.
Le JSON sera utilisé par les outils de pyautogui et opencv de python.

fichiers images: """ + str(images) + """
fichiers cascades: """ + str(cascades) + """

répondre seulement en json sous ce format sans commentaires et sans formatage ```json ```:
{"instructions":
    {<graphe>},
"message suplémentaire de chatgpt": "<message>"
}
Donner le json permettant de:


"""
