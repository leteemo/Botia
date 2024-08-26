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
        for port in self.input_ports():
            for connected_port in port.connected_ports():
                parent_node = connected_port.node()
                if(parent_node.getValue() != None and val != None):
                    val[0] += float(parent_node.getValue()[0])
                    val[1] += float(parent_node.getValue()[1])

        return val
    

