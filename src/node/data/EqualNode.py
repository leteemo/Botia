from node.Node import Node
import pyautogui

class EqualNode(Node):
    __identifier__ = 'data'  # Identifiant du noeud
    NODE_NAME = 'EqualNode'       # Nom du noeud

    def __init__(self):
        super(EqualNode, self).__init__()

        # Ajout de ports d'entrée et de sortie
        self.add_input('data')
        self.add_input('data2')
        self.add_output('result')

        self.value = None

    def getValue(self):

        # On cherche la valeurs retournées par les ports connectés
        port1 = self.get_input("data").connected_ports()[0]
        port2 = self.get_input("data2").connected_ports()[0]

        port1.node().getValue()
        port2.node().getValue()

        setattr(self.get_output("result"), 'data', port1.data == port2.data)


