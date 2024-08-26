from node.Node import Node
import pyautogui

class KeyNode(Node):
    __identifier__ = 'action'  # Identifiant du noeud
    NODE_NAME = 'KeyNode'       # Nom du noeud

    def __init__(self):
        super(KeyNode, self).__init__()

        # Ajout de ports d'entrée et de sortie
        self.add_input('input')
        self.add_output('output')
        self.add_text_input('key', label='key', tooltip=None, tab=None)


    def action(self):
        print("execution key")
        pyautogui.typewrite(self.get_property('key'))

