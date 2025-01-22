from node.Node import Node
import pyautogui


class ScrollNode(Node):
    __identifier__ = 'action'  # Identifiant du noeud
    NODE_NAME = 'ScrollNode'       # Nom du noeud

    def __init__(self):
        super(ScrollNode, self).__init__()

        self.add_text_input("scroll value", label='scroll value', tooltip=None, tab=None)

        # Ajout de ports d'entrée et de sortie
        self.add_input('input')
        self.add_output('output')

    def action(self):
        print("execution scroll")
        pyautogui.scroll(int(self.get_property('scroll value')))