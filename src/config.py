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
        dossier = 'images/'
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



def get_exemples(dossier, fichiers=[]):

    contenu_total = ""

    if len(fichiers) == 0:
        fichiers = os.listdir(dossier)


    for fichier in fichiers:

        if fichier.endswith(".json"):
            chemin_fichier = os.path.join(dossier, fichier)
            with open(chemin_fichier, "r", encoding="utf-8") as f:
                contenu_total += f.read() + "\n autre exemple: \n"

    return contenu_total


INIT_PROMPT = """L'objectif est de  te baser sur cet exemple de structure json afin de me renvoyer des instructions comme par exemple:

""" + get_exemples("saves", fichiers=["ai.json", "cascadeloop.json", "click_firefox.json", "windows_click", "search.json"]) + """

liste des neouds: action.GetAIObjectCoordNode, action.KeyNode, action.GetImageCoordNode, control.DelayNode, action.GetImageCoordNode, action.MoveMouseNode, control.DelayNode,
action.GetImageFromSearch.

GetImageFromSearch: cherche sur internet une image et la compare grâce au match de points d'interets, efficace pour les images 2D comme les icones, dessin 2D, photos récurentes etc...
GetAIObjectCoordNode: utilise une ia multimodal pour analyser une image, efficace pour les objets 3D qui peuvent tourner sur 3 dimensions comme des objets du quotidien.
GetImageCoordNode: Cherche image exacte avec un degré de différence.
If: condition, pour par exemple vérifier que un node renvoie quelque chose, utilise le pour bien vérifier afin de ne pas faire crash.

Il faut être très exacte sur le type et l'identifier, c'est à dire en fonction du __identifier__, il n'y a que action, control et data.
C'est un graphe où tu peux mettre le nom que tu veux pour les node, les "type" permettent de donner l'action effectué par le node.
coord permet de placer le node dans l'interface graphique.
Le premier node devra être un Start.
Un input ne peut être connecté qu'à un output.
Le JSON sera utilisé par les outils de pyautogui et opencv de python.


fichiers images: """ + str(images) + """
fichiers cascades: """ + str(cascades) + """

répondre seulement en json sous ce format sans commentaires et sans aucun formatage de type ```json ```:
{"instructions":
    {<graphe>},
"message suplémentaire de chatgpt": "<message>"
}
Donner le json permettant de:


"""
