from node.Node import Node
import pyautogui

class FloatNode(Node):
    __identifier__ = 'data'  # Identifiant du noeud
    NODE_NAME = 'FloatNode'       # Nom du noeud

    def __init__(self):
        super(FloatNode, self).__init__()

        # Ajout de ports de sortie
        self.add_output('output')

        self.add_text_input('float', label='float', tooltip=None, tab=None)


    def getValue(self):
        return float(self.get_property('float'))




