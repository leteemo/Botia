from node.Node import Node
import pyautogui


class ForLoopNode(Node):
    __identifier__ = 'controll'  # Identifiant du noeud
    NODE_NAME = 'ForLoopNode'       # Nom du noeud

    def __init__(self):
        super(ForLoopNode, self).__init__()

        # Ajout de ports d'entrée et de sortie
        self.add_input('input')
        self.add_output('output')
        

    def action(self):

        print("execution branching")
        nodes_end = self.getAllEndNodes(self)
        self.setNodesBranch(nodes_end)


    def setNodesBranch(self, nodes_end):
        for node in nodes_end:
            node.setBranching(self)
            

    def getAllEndNodes(self, node):
        descendants = []
        for output_port in node.output_ports():
            for connected_port in output_port.connected_ports():
                child_node = connected_port.node()
                if child_node not in descendants:
                    descendants.append(child_node)
                    descendants.extend(self.getAllEndNodes(child_node))
        return descendants

            
            
