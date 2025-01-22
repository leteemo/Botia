from node.Node import Node
import pyautogui


class ForEachLoopNode(Node):
    __identifier__ = 'control'  # Identifiant du noeud
    NODE_NAME = 'ForEachLoopNode'       # Nom du noeud
    number_iteration = 0
    stop = False

    def __init__(self):
        super(ForEachLoopNode, self).__init__()

        # Ajout de ports d'entrée et de sortie
        self.add_input('input')
        self.add_output('output')

        self.add_input('array')
        self.add_output('returned data')

        self.add_output('end_output')

        

    def action(self):
        print("execution for loop")

        # Chargement de la valeur dans l'attribut data du port <returned data>
        array = self.get_input("array").connected_ports()[0].data

        if len(array) > 0:
            setattr(self.get_output("returned data"), 'data', array[ForEachLoopNode.number_iteration])
            

            maximum_iteration = int(len(self.get_input("array").connected_ports()[0].data))
            
            if ForEachLoopNode.number_iteration == maximum_iteration-1:
                ForEachLoopNode.stop = True

            if ForEachLoopNode.number_iteration < maximum_iteration-1:
                nodes_end = self.getAllEndNodes(self)
                self.setNodesBranch(nodes_end, self)
                ForEachLoopNode.number_iteration += 1

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
        if not ForEachLoopNode.stop:
            super().execute()
        else:
            self.action()
            
    def reinit():
        ForEachLoopNode.number_iteration = 0
        ForEachLoopNode.stop = False