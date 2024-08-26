from node.Node import Node

class StartNode(Node):
    __identifier__ = 'start'  # Identifiant du noeud
    NODE_NAME = 'StartNode'   # Nom du noeud

    def __init__(self):
        super(StartNode, self).__init__()

        # Ajout de ports de sortie
        self.add_output('output')

    def action(self):
        print("execution start")
