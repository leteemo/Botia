from NodeGraphQt import BaseNode

class Node(BaseNode):
    def __init__(self, *args, **kwargs):
        super(Node, self).__init__(*args, **kwargs)
        self.botManager = None
        self.graph_n = None
        self.branch = None

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

        if len(self.get_output("output").connected_ports()) > 0:
            self.botManager.addNodeToQueue(self.get_output("output").connected_ports()[0].node())
        elif self.branch != None:
            self.botManager.addNodeToQueue(self.branch)

    def getValue(self):
        pass





