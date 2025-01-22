from node.Node import Node
import pyautogui

class AddArray2DNode(Node):
    __identifier__ = 'data'  # Identifiant du noeud
    NODE_NAME = 'AddArray2DNode'       # Nom du noeud

    def __init__(self):
        super(AddArray2DNode, self).__init__()

        # Ajout de ports d'entrée et de sortie
        self.add_input('data')
        self.add_input('data2')
        self.add_output('output')

        self.value = None

    def getValue(self):
        val = [0, 0]
        self.get_input("data").connected_ports()[0].node().getValue()
        self.get_input("data2").connected_ports()[0].node().getValue()

        value1 = self.get_input("data").connected_ports()[0].data
        value2 = self.get_input("data2").connected_ports()[0].data
        
        val[0] = value1[0] + value2[0]
        val[1] = value1[1] + value2[1]

        setattr(self.get_output("output"), 'data', val)
    

