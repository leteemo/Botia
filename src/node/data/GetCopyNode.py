from node.Node import Node
import pyautogui

class GetCopyNode(Node):
    __identifier__ = 'data'  # Identifiant du noeud
    NODE_NAME = 'GetCopyNode'       # Nom du noeud

    def __init__(self):
        super(GetCopyNode, self).__init__()

        # Ajout de ports de sortie
        self.add_input('data')
        self.add_output('extracted data')

        self.add_text_input('index', label='index', tooltip=None, tab=None)


    def getValue(self):
        setattr(self.get_output("extracted data"), 'data', self.get_input("data").connected_ports()[0].data[int(self.get_property('index'))])





