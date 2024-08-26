from PySide2.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QAction, QFileDialog, QMessageBox
from PySide2.QtGui import QKeyEvent
from PySide2.QtCore import Qt

from NodeGraphQt import NodeGraph, BaseNode

from node.StartNode import StartNode
from node.MoveMouseNode import MoveMouseNode
from node.KeyNode import KeyNode
from node.DelayNode import DelayNode
from node.MoveToImageNode import MoveToImageNode
from node.ClickMouseNode import ClickMouseNode
from node.ScrollNode import ScrollNode
from node.BranchNode import BranchNode
from node.ForLoopNode import ForLoopNode
from node.data.FloatNode import FloatNode
from node.data.AddFloatNode import AddFloatNode
from node.data.Array2DNode import Array2DNode
from node.data.AddArray2DNode import AddArray2DNode


import threading
import json
import sys
import time

class BotManager:
    thread = None
    queue = []
    keep_execution = True

    def addActionToQueue(self, action):
        BotManager.queue.append(action)

    def startBot(self):
        BotManager.keep_execution = True
        if BotManager.thread == None:
            BotManager.thread = threading.Thread(target=BotManager.execute)
            BotManager.thread.start()

    def stopBot(self):
        BotManager.keep_execution = False

    def execute():
        while BotManager.keep_execution and len(BotManager.queue) > 0:
            BotManager.queue[0].execute()
            BotManager.queue.pop(0)
        
        BotManager.thread = None

    def setQueue(queue):
        BotManager.queue = queue
    


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.botManager = BotManager()

        # Initialisation du graphe de noeuds
        self.graph = NodeGraph()
        self.graph.set_acyclic(False)
        self._register_nodes()

        # Création et positionnement du noeud de départ
        self.start_node = self._create_node('start.StartNode', 'Start', 150, 150)

        # Configuration de l'interface utilisateur
        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)
        self.setCentralWidget(central_widget)
        main_layout.addWidget(self.graph.widget)
        main_layout.addWidget(self._create_button_widget())

        # Configuration de la fenêtre principale
        self.setWindowTitle('NodeGraphQt with PySide2 and Buttons')
        self.resize(1500, 900)
        self.load_stylesheet("style.css")

        # Ajout du menu
        self._create_menu()

    def _register_nodes(self):
        nodes = [StartNode, MoveMouseNode, KeyNode, DelayNode, MoveToImageNode, ClickMouseNode, ScrollNode, BranchNode, ForLoopNode, FloatNode, AddFloatNode, Array2DNode, AddArray2DNode]
        for node in nodes:
            self.graph.register_node(node)

    def _create_node(self, node_type, name, x, y, color='#606060'):
        node = self.graph.create_node(node_type, name=name, color=color)
        node.setBotManager(self.botManager)
        node.set_pos(x, y)
        return node

    def _create_button_widget(self):
        button_widget = QWidget()
        button_layout = QVBoxLayout(button_widget)

        buttons = [
            ("Add Move Mouse", lambda: self._create_node('action.MoveMouseNode', 'Move Mouse', 500, 300)),
            ("Add Key", lambda: self._create_node('action.KeyNode', 'Key', 500, 300)),
            ("Add Delay", lambda: self._create_node('controll.DelayNode', 'Delay', 500, 300)),
            ("Add Move To Image", lambda: self._create_node('action.MoveToImageNode', 'Move To Image', 500, 300)),
            ("Add Click Mouse", lambda: self._create_node('action.ClickMouseNode', 'Click Mouse', 500, 300)),
            ("Add Scroll", lambda: self._create_node('action.ScrollNode', 'Scroll', 500, 300)),
            ("Add Branch", lambda: self._create_node('controll.BranchNode', 'Branch to Node', 500, 300).setGraph(self.graph)),
            ("Add For Loop", lambda: self._create_node('controll.ForLoopNode', 'For Loop', 500, 300)),
            ("Add Float", lambda: self._create_node('data.FloatNode', 'Add float', 500, 300)),
            ("Add Float addition", lambda: self._create_node('data.AddFloatNode', 'Float', 500, 300)),
            ("Add Array 2D", lambda: self._create_node('data.Array2DNode', 'Array2DNode', 500, 300)),
            ("Add Array 2D Addition", lambda: self._create_node('data.AddArray2DNode', 'AddArray2DNode', 500, 300)),
            ("execute", self.firstExecution, "background-color: rgb(0,255,0);"),
            ("stop", self.stopExecution, "background-color: rgb(255,0,0);")
        ]

        for text, method, *style in buttons:
            button = QPushButton(text)
            if style:
                button.setStyleSheet(style[0])
            button.clicked.connect(method)
            button_layout.addWidget(button)

        return button_widget

    def _create_menu(self):
        menu = self.menuBar().addMenu("File")
        menu.addAction(QAction("Save as...", self, triggered=self.saveToJSON))
        menu.addAction(QAction("Load file", self, triggered=self.readFile))

    def firstExecution(self):
        BotManager.setQueue([])
        self.botManager.addActionToQueue(self.graph.get_node_by_name('Start'))
        self.botManager.startBot()




    def stopExecution(self):
        self.botManager.stopBot()

    def load_stylesheet(self, path):
        """Charge un fichier de stylesheet et l'applique à l'application."""
        with open(path, "r") as file:
            stylesheet = file.read()
            self.setStyleSheet(stylesheet)

    def keyPressEvent(self, event: QKeyEvent):
        # Vérifiez si la touche 'y' est pressée
        if event.key() == Qt.Key_X or event.key() == Qt.Key_Delete:
            for node in self.graph.selected_nodes():
                self.graph.delete_node(node)

        if event.key() == Qt.Key_F:
            self.botManager.stopBot()

        if event.key() == Qt.Key_S:
            self.botManager.startBot()

    def saveToJSON(self):
        data = {}

        for node in self.graph.all_nodes():
            inputs = {}
            outputs = {}

            for outp in node.output_ports():
                list_output_connexions = []
                for inp_node in outp.connected_ports():
                    list_output_connexions.append({"connected node":inp_node.node().name(), "connected input":inp_node.name()})
                
                outputs[outp.name()] = list_output_connexions

            for inp in node.inputs():
                inputs[inp] = inp

            widgets = {}
            for widget in node.widgets():
                widgets[widget] = node.get_property(widget)

            data[node.name()] = {"inputs":inputs, "outputs":outputs, "widgets":widgets, "coord":{"x":node.pos()[0], "y":node.pos()[1]}, "type":type(node).__name__, "identifier":node.__identifier__}

        # Nom de fichier par défaut
        default_file = "saves/data.json"

        # Ouvrir une boîte de dialogue pour choisir l'emplacement et le nom du fichier
        file, _ = QFileDialog.getSaveFileName(self, "Save file", default_file, "JSON Files (*.json)")

        # Vérifier si l'utilisateur a sélectionné un fichier
        if file:
            try:
                # Écrire les données dans le fichier JSON
                with open(file, 'w') as f:
                    json.dump(data, f, indent=4)


            except Exception as e:
                # En cas d'erreur, afficher un message d'erreur
                QMessageBox.critical(self, "Error", f"Error : {e}")

    def readFile(self):
        # Ouvrir une boîte de dialogue pour choisir l'emplacement et le nom du fichier
        file, _ = QFileDialog.getOpenFileName(self, "Load from a file", "", "JSON file (*.json);;All files (*)")
        with open(file, 'r', encoding='utf-8') as file_json:
            data = json.load(file_json)
            self.loadFromJSON(data)

    def loadFromJSON(self, json):

        self.eraseAllNodes()

        # Effacer tous les nodes
        for node in json:
            node_obj = self.graph.create_node(json[node]["identifier"] + "." + json[node]["type"], name=node, color='#606060')
            node_obj.set_pos(json[node]["coord"]["x"], json[node]["coord"]["y"])
            node_obj.setBotManager(self.botManager)
            node_obj.setGraph(self.graph)

            if("widgets" in json[node]):
                for widget_name, widget_value in json[node]["widgets"].items():
                    node_obj.get_widget(widget_name).set_value(widget_value)
        
        for node in json:
            for output in json[node]["outputs"]:
                if len(json[node]["outputs"][output]) > 0:
                    node_obj = self.graph.get_node_by_name(node)
                    node_target_obj = self.graph.get_node_by_name(json[node]["outputs"][output][0]["connected node"])
                    input_target = json[node]["outputs"][output][0]["connected input"]
                    output_target_index = self.get_output_index_by_name(node_obj, output)
                    node_obj.set_output(output_target_index, node_target_obj.inputs().get(input_target))

            

    def eraseAllNodes(self):
        # Effacer tous les nodes
        for node in self.graph.all_nodes():
            self.graph.delete_node(node)

    def get_output_index_by_name(self, node, output_name):

        outputs_list = node.outputs()
        for i, port in enumerate(outputs_list.values()):
            if port.name() == output_name:
                return i
        return None




if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Créer et afficher la fenêtre principale
    main_window = MainWindow()
    main_window.show()

    sys.exit(app.exec_())


