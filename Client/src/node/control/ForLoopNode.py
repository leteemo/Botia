from node.Node import Node
import pyautogui


class ForLoopNode(Node):
    __identifier__ = 'control'  # Identifiant du noeud
    NODE_NAME = 'ForLoopNode'       # Nom du noeud
    number_iteration = 0
    stop = False

    def __init__(self):
        super(ForLoopNode, self).__init__()

        # Ajout de ports d'entrée et de sortie
        self.add_input('input')
        self.add_output('output')

        self.add_output('end_output')

        self.add_text_input('begin', label='begin', tooltip=None, tab=None)
        self.add_text_input('end', label='end', tooltip=None, tab=None)
        

    def action(self):
        print("execution for loop")
        ForLoopNode.number_iteration = int(self.get_property('begin')) + ForLoopNode.number_iteration
        maximum_iteration = int(self.get_property('end'))
        
        if ForLoopNode.number_iteration == maximum_iteration:
            ForLoopNode.stop = True

        if ForLoopNode.number_iteration <= maximum_iteration:
            nodes_end = self.getAllEndNodes(self)
            self.setNodesBranch(nodes_end, self)
            ForLoopNode.number_iteration += 1

        else:
            nodes_end = self.getAllEndNodes(self)
            self.setNodesBranch(nodes_end, None)

            if len(self.get_output("end_output").connected_ports()) > 0:
                self.botManager.addNodeToQueue(self.get_output("end_output").connected_ports()[0].node())


    def setNodesBranch(self, nodes_end, branchedNode):
        for node in nodes_end:
            node.setBranching(branchedNode)
            

    def getAllEndNodes(self, node):
        descendants = []
        for output_port in node.output_ports():
            for connected_port in output_port.connected_ports():
                child_node = connected_port.node()
                if child_node not in descendants:
                    descendants.append(child_node)
                    descendants.extend(self.getAllEndNodes(child_node))
        return descendants


    def execute(self):
        if not ForLoopNode.stop:
            super().execute()
        else:
            self.action()
            
    def reinit():
        ForLoopNode.number_iteration = 0
        ForLoopNode.stop = False