from node.Node import Node
import time

class DelayNode(Node):
    __identifier__ = 'controll'  # Identifiant du noeud
    NODE_NAME = 'DelayNode'       # Nom du noeud

    def __init__(self):
        super(DelayNode, self).__init__()

        self.add_text_input("delay", label='delay (seconds)', tooltip=None, tab=None)

        # Ajout de ports d'entrée et de sortie
        self.add_input('input')
        self.add_output('output')
        
    def action(self):
        print("execution delay")
        time.sleep(int(self.get_property('delay')))