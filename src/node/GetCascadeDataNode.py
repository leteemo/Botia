import pyautogui
from node.Node import Node
import cv2
import numpy as np

class GetCascadeDataNode(Node):
    __identifier__ = 'control'  # Identifiant du noeud
    NODE_NAME = 'GetCascadeDataNode'       # Nom du noeud

    def __init__(self):
        super(GetCascadeDataNode, self).__init__()

        # Ajout de ports d'entrée et de sortie
        self.add_input('input', multi_input=True)
        self.add_output('output')
        self.add_output('coords of detected')
        
        #self.add_checkbox('cb_1', '', 'Checkbox 1', True)
        self.add_text_input('cascade file', label='cascade file', tooltip=None, tab=None)
        self.add_text_input('scale factor', label='scale factor', text="1.1", tooltip=None, tab=None)
        self.add_text_input('min neighboor', label='min neighboor', text="10", tooltip=None, tab=None)

        self.botManager = None

        self.value = None


    def action(self):
        self.setCoordsData()

        
    def setCoordsData(self):
        # Charger le classificateur de cascade de Haar
        cascade_path = self.get_property('cascade file')
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + cascade_path)

        # Charger une image
        image = pyautogui.screenshot()

        # Convertir l'image PIL en tableau NumPy
        image_np = np.array(image)

        # Convertir du format RGB (PIL) à BGR (OpenCV)
        image_cv = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)

        # Convertir l'image en niveaux de gris
        gray = cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY)


        # Détecter les objets
        detected_objects = face_cascade.detectMultiScale(
            gray,
            scaleFactor=float(self.get_property('scale factor')),  # Paramètre d'échelle pour la réduction de taille
            minNeighbors=int(self.get_property('min neighboor')),   # Paramètre pour filtrer les faux positifs
            minSize=(30, 30), # Taille minimale de l'objet détecté
            flags=cv2.CASCADE_SCALE_IMAGE
        )

        list_objects = []

        # Afficher les objets détectés
        for (x, y, w, h) in detected_objects:
            list_objects.append([x, y, x+w, y+h])

        setattr(self.get_output("coords of detected"), 'data', list_objects)