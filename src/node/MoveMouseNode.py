import pyautogui
from node.Node import Node


class MoveMouseNode(Node):
    __identifier__ = 'action'  # Identifiant du noeud
    NODE_NAME = 'MoveMouseNode'       # Nom du noeud

    def __init__(self):
        super(MoveMouseNode, self).__init__()


        # Ajout de ports d'entrée et de sortie
        self.add_input('input')
        self.add_output('output')
        
        self.add_text_input('coor x', label='coor x', tooltip=None, tab=None)
        self.add_text_input("coor y", label='coor y', tooltip=None, tab=None)

        self.add_input('data')

        self.x = None
        self.y = None

    def action(self):

        # Défini les valeurs de x et y si elles sont renseignées
        if self.get_property('coor x') and self.get_property('coor y'):
            self.x = self.get_property('coor x')
            self.y = self.get_property('coor y')

        if len(self.get_input("data").connected_ports()) > 0:
            self.get_input("data").connected_ports()[0].node().getValue()
            self.x, self.y = self.get_input("data").connected_ports()[0].data

        if self.x and self.y:
            pyautogui.moveTo(int(self.x), int(self.y))

        print("execution mouse move", self.x, self.y)


    def on_input_connected(self, in_port, out_port):
        if in_port.name() == "data":
            self.get_widget("coor x").setVisible(False)
            self.get_widget("coor y").setVisible(False)

    def on_input_disconnected(self, in_port, out_port):
        if in_port.name() == "data":
            self.get_widget("coor x").setVisible(True)
            self.get_widget("coor y").setVisible(True)



