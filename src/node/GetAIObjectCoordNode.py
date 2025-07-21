import pyautogui
from node.Node import Node
import mss
import numpy as np
import matplotlib.pyplot as plt
import io
import requests
from PIL import Image
import base64
import os
import pyautogui
import json
import mss

class GetAIObjectCoordNode(Node):
    __identifier__ = 'action'  # Identifiant du noeud
    NODE_NAME = 'GetAIObjectCoordNode'       # Nom du noeud

    def __init__(self):
        super(GetAIObjectCoordNode, self).__init__()

        # Ajout de ports d'entrée et de sortie
        self.add_input('input', multi_input=True)
        self.add_output('output')
        self.add_output('data')
        
        self.add_text_input('prompt', label='prompt', tooltip=None, tab=None)

        self.botManager = None

        self.value = None

    def getValue(self):

        self.value = capture_and_send_to_ai(prompt=self.get_property('prompt'))
        setattr(self.get_output("data"), 'data', self.value)
        
def case_to_xy(case_label, img_width, img_height, num_cells_x, num_cells_y):
    """
    Convertit un label de case en coordonnées x, y du centre de la case.

    Args:
        case_label (str): Label de la case, ex. "A1", "C7", etc.
        img_width (int): Largeur de l'image en pixels.
        img_height (int): Hauteur de l'image en pixels.
        num_cells_x (int, optional): Nombre de colonnes (cells) en X. Default = 10.
        num_cells_y (int, optional): Nombre de lignes (cells) en Y. Default = 10.

    Returns:
        tuple: (x_center, y_center) en pixels, ou lève ValueError si le label est invalide.
    """
    # Validation basique du format : une lettre + un ou plusieurs chiffres
    import re
    match = re.fullmatch(r'([A-Za-z])(\d+)', case_label.strip())
    if not match:
        raise ValueError(f"Format de case invalide : {case_label!r}")

    row_letter, col_str = match.groups()
    row_index = ord(row_letter.upper()) - ord('A')  # A → 0, B → 1, etc.
    col_index = int(col_str) - 1                   # "1" → 0, "2" → 1, etc.

    if not (0 <= row_index < num_cells_y) or not (0 <= col_index < num_cells_x):
        raise ValueError(f"Case hors grille : {case_label!r}")

    # Taille d'une cellule
    cell_w = img_width  / num_cells_x
    cell_h = img_height / num_cells_y

    # Coordonnées du centre
    x_center = col_index * cell_w + cell_w / 2
    y_center = row_index * cell_h + cell_h / 2

    return x_center, y_center

def capture_and_send_to_ai(prompt="",
        save_path="screenshot_with_axes.png",
        num_cells_x=8,
        num_cells_y=8,
        dpi=130,
        openai_api_key=None,
        model="gpt-4.1-nano",
        add_grid=True
    ):

    prompt += """Donne la case où se la chose demandée au format json sans formatage, exemple de reponse de format à respecter: {"case": "A1"}, Si il n'y a pas, renvoie {"case":"None"}"""

    if not openai_api_key:
        openai_api_key = os.getenv("OPENAI_API_KEY")


    # Capture d'écran
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        sct_img = sct.grab(monitor)

    img = np.array(sct_img)[..., :3][..., ::-1]
    height, width, _ = img.shape

    # Création de la figure avec axes
    fig, ax = plt.subplots(figsize=(width/dpi, height/dpi), dpi=dpi)
    ax.imshow(img)
    ax.set_xlim(0, width)
    ax.set_ylim(height, 0)

    # Ajout des labels de case pour les axes X (colonnes) et Y (lignes)
    cell_width = width / num_cells_x
    cell_height = height / num_cells_y

    # Positions des ticks au centre de chaque cellule
    xticks = [(i + 0.5) * cell_width for i in range(num_cells_x)]
    yticks = [(j + 0.5) * cell_height for j in range(num_cells_y)]

    # Labels des ticks : 1, 2, 3... pour X ; A, B, C... pour Y
    xtick_labels = [str(i + 1) for i in range(num_cells_x)]
    ytick_labels = [chr(65 + j) for j in range(num_cells_y)]

    ax.set_xticks(xticks)
    ax.set_xticklabels(xtick_labels, fontsize=7)
    ax.set_yticks(yticks)
    ax.set_yticklabels(ytick_labels, fontsize=7)

    ax.set_xlabel("Colonnes")
    ax.set_ylabel("Lignes")

    # Ajout de la grille alphanumérique
    cell_width = width / num_cells_x
    cell_height = height / num_cells_y

    if add_grid:
        for i in range(num_cells_x + 1):
            ax.axvline(i * cell_width, color='gray', linestyle='--', linewidth=0.5)
        for j in range(num_cells_y + 1):
            ax.axhline(j * cell_height, color='gray', linestyle='--', linewidth=0.5)

        for j in range(num_cells_y):
            for i in range(num_cells_x):
                label = f"{chr(65 + j)}{i + 1}"
                x = i * cell_width + cell_width / 2
                y = j * cell_height + cell_height / 2
                ax.text(x, y, label, color='white', ha='center', va='center', fontsize=15,
                        bbox=dict(facecolor='black', alpha=0.7, boxstyle='round,pad=0.2'))

    # Sauvegarde image
    buf = io.BytesIO()
    plt.savefig(save_path, format='png', dpi=dpi, bbox_inches='tight', pad_inches=0)
    plt.savefig(buf, format='png', dpi=dpi, bbox_inches='tight', pad_inches=0)
    plt.close(fig)
    buf.seek(0)


    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    image_url = f"data:image/png;base64,{image_base64}"

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
            "Authorization": f"Bearer {openai_api_key}",
            "Content-Type": "application/json"
    }

    payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": image_url}}
                    ]
                }
            ],
            "temperature":0 
    }

    response = requests.post(url, headers=headers, json=payload)

    if not response.ok:
        print("Erreur API :", response.status_code, response.text)
        return

    result = response.json()
    content = result["choices"][0]["message"]["content"]
    print(content)

    try:

        coords = json.loads(content)
        print(f"Coordonnées détectées : {coords}")

        label = coords["case"]

        if "case" in coords:
            x, y = case_to_xy(label, width, height,
                            num_cells_x=num_cells_x,
                            num_cells_y=num_cells_y)

            return (int(x), int(y))


    except Exception as e:
        print("Erreur dans l’analyse ou le déplacement :", e)

    return None

    
