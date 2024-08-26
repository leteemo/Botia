from node.Node import Node
import pyautogui

class Array2DNode(Node):
    __identifier__ = 'data'  # Identifiant du noeud
    NODE_NAME = 'Array2DNode'       # Nom du noeud

    def __init__(self):
        super(Array2DNode, self).__init__()

        # Ajout de ports d'entrée et de sortie
        self.add_input('data x')
        self.add_input('data y')
        self.add_output('output')

        self.value = None

    def getValue(self):
        val = []
        for port in self.input_ports():
            for connected_port in port.connected_ports():
                parent_node = connected_port.node()
                val.append(parent_node.getValue())

        return val
    

