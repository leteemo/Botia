from NodeGraphQt import BaseNode

class Node(BaseNode):
    def __init__(self, *args, **kwargs):
        super(Node, self).__init__(*args, **kwargs)
        self.botManager = None # Interpreter
        self.graph_n = None # Graph contenant les nodes
        self.branch = None # Node utilisé pour le branchment

    def setBotManager(self, BotManager):
        self.botManager = BotManager

    def setGraph(self, graph):
        self.graph_n = graph

    def setBranching(self, branch):
        self.branch = branch

    def action(self):
        print("execution" + self.name())

    def execute(self):

        self.action()

        # Si il y a un output avec un node connecté, ajouter le prochain node à la queue
        if len(self.get_output("output").connected_ports()) > 0:
            self.botManager.addNodeToQueue(self.get_output("output").connected_ports()[0].node())
        # Si un branchement est défini, ajouter le node à brancher à la queue
        elif self.branch != None:
            self.botManager.addNodeToQueue(self.branch)

    def getValue(self):
        pass





