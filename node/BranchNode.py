from node.Node import Node
import pyautogui


class BranchNode(Node):
    __identifier__ = 'controll'  # Identifiant du noeud
    NODE_NAME = 'BranchNode'       # Nom du noeud

    def __init__(self):
        super(BranchNode, self).__init__()

        # Ajout de ports d'entrée et de sortie
        self.add_input('input')
        self.add_output('output')

        self.add_text_input("name of node", label='name of node', tooltip=None, tab=None)
        

    def execute(self):

        print("execution branching")

        if len(self.get_property('name of node')) > 0 and self.graph_n != None:
            self.botManager.addActionToQueue(self.graph_n.get_node_by_name(self.get_property('name of node')))
            
