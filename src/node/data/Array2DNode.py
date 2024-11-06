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
        self.add_output('data 2D')

        self.add_text_input('coor x', label='coor x', tooltip=None, tab=None)
        self.add_text_input("coor y", label='coor y', tooltip=None, tab=None)

        self.x = None
        self.y = None


    def getValue(self):

        if len(self.get_input("data x").connected_ports()) == 0:
            self.x = self.get_property('coor x')
        else:
            self.get_input("data x").connected_ports()[0].node().getValue()
            self.x = self.get_input("data x").connected_ports()[0].data

        if len(self.get_input("data y").connected_ports()) == 0:
            self.y = self.get_property('coor y')
        else:
            self.get_input("data y").connected_ports()[0].node().getValue()
            self.y = self.get_input("data y").connected_ports()[0].data

        setattr(self.get_output("data 2D"), 'data', [self.x, self.y])


    def on_input_connected(self, in_port, out_port):
        if in_port.name() == "data x":
            self.get_widget("coor x").setVisible(False)
        if in_port.name() == "data y":
            self.get_widget("coor y").setVisible(False)

    def on_input_disconnected(self, in_port, out_port):
        if in_port.name() == "data x":
            self.get_widget("coor x").setVisible(True)
        if in_port.name() == "data y":
            self.get_widget("coor y").setVisible(True)
