import pyautogui
from node.Node import Node


class IfNode(Node):
    __identifier__ = 'control'  # Identifiant du noeud
    NODE_NAME = 'IfNode'       # Nom du noeud

    def __init__(self):
        super(IfNode, self).__init__()

        # Ajout de ports d'entrée et de sortie
        self.add_input('input')
        self.add_output('true')
        self.add_output('false')
        
        items = ['True', 'False']
        self.add_combo_menu('boolean', 'boolean', items)

        self.add_input('data')

        self.data = True

    def action(self):
        
        # Défini la valeur booléenne
        if self.get_property('boolean'):
            self.data = self.get_property('boolean') == "True"

        # Défini la valeur booléenne
        if len(self.get_input("data").connected_ports()) > 0:
            self.get_input("data").connected_ports()[0].node().getValue()
            self.data = self.get_input("data").connected_ports()[0].data

        print("execution if branch", self.data)


    def on_input_connected(self, in_port, out_port):
        if in_port.name() == "data":
            self.get_widget("boolean").setVisible(False)

    def on_input_disconnected(self, in_port, out_port):
        if in_port.name() == "data":
            self.get_widget("boolean").setVisible(True)


    def execute(self):

        self.action()

        # Ajout du prochain node dans la queue
        if self.data and len(self.get_output("true").connected_ports()) > 0:
            self.botManager.addNodeToQueue(self.get_output("true").connected_ports()[0].node())
            return

        elif not self.data and len(self.get_output("false").connected_ports()) > 0:
            self.botManager.addNodeToQueue(self.get_output("false").connected_ports()[0].node())
            return
