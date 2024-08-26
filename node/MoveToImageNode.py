import pyautogui
from node.Node import Node


class MoveToImageNode(Node):
    __identifier__ = 'action'  # Identifiant du noeud
    NODE_NAME = 'MoveToImageNode'       # Nom du noeud

    def __init__(self):
        super(MoveToImageNode, self).__init__()

        # Ajout de ports d'entrée et de sortie
        self.add_input('input', multi_input=True)
        self.add_output('output')
        self.add_output('data')
        
        #self.add_checkbox('cb_1', '', 'Checkbox 1', True)
        self.add_text_input('image src', label='image src', tooltip=None, tab=None)
        self.add_text_input('precision', label='precision', text="1", tooltip=None, tab=None)

        self.botManager = None

        self.value = None


    def getValue(self):
        self.value = pyautogui.locateCenterOnScreen(self.get_property('image src'),  confidence=float(self.get_property('precision')))
        return self.value
        
