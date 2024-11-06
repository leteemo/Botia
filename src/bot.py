from PySide2.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QAction, QFileDialog, QMessageBox, QLineEdit, QTextEdit, QTreeWidget, QTreeWidgetItem
from PySide2.QtGui import QKeyEvent
from PySide2.QtCore import Qt

from NodeGraphQt import NodeGraph, BaseNode

from node.StartNode import StartNode
from node.MoveMouseNode import MoveMouseNode
from node.KeyNode import KeyNode
from node.DelayNode import DelayNode
from node.GetImageCoordNode import GetImageCoordNode
from node.ClickMouseNode import ClickMouseNode
from node.ScrollNode import ScrollNode

from node.BranchNode import BranchNode
from node.ForLoopNode import ForLoopNode
from node.ForEachLoopNode import ForEachLoopNode

from node.GetCascadeDataNode import GetCascadeDataNode
from node.data.FloatNode import FloatNode
from node.data.AddFloatNode import AddFloatNode
from node.data.Array2DNode import Array2DNode
from node.data.AddArray2DNode import AddArray2DNode
from node.data.GetCopyNode import GetCopyNode

from node.GetSearchedImageCoordNode import GetSearchedImageCoordNode

import threading
import json
import sys
import time
import requests

from apikey import API_KEY
from config import INIT_PROMPT



class BotManager:
    thread = None
    queue = []
    keep_execution = True

    def addNodeToQueue(self, action):
        BotManager.queue.append(action)

    def startBot(self):
        BotManager.keep_execution = True
        if BotManager.thread == None:
            BotManager.thread = threading.Thread(target=BotManager.execute)
            BotManager.thread.start()

    def stopBot(self):
        BotManager.keep_execution = False
        ForLoopNode.reinit()
        ForEachLoopNode.reinit()

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
        self.main_layout = QHBoxLayout(central_widget)
        self.setCentralWidget(central_widget)

        self._create_button_widget()


        # Configuration de la fenêtre principale
        self.setWindowTitle('Botia')
        self.resize(1500, 900)
        self.load_stylesheet("style.css")

        # Ajout du menu
        self._create_menu()

        # Stocker les reponses des llm
        self.response_llm = ""


    # Enregistrement des nodes dans le graphe
    def _register_nodes(self):
        nodes = [StartNode, MoveMouseNode, KeyNode, DelayNode, GetImageCoordNode, ClickMouseNode, ScrollNode, GetSearchedImageCoordNode,
            BranchNode, ForLoopNode, ForEachLoopNode, GetCascadeDataNode, FloatNode, AddFloatNode, Array2DNode, AddArray2DNode, GetCopyNode]
        for node in nodes:
            self.graph.register_node(node)

    # Ajout d'un nodes dans l'interface graphique
    def _create_node(self, node_type, name, x, y, color='#606060'):
        node = self.graph.create_node(node_type, name=name, color=color)
        node.setBotManager(self.botManager)
        node.set_pos(x, y)
        return node

    def filter_buttons(self):
        search_text = self.search_input.text().lower()

        for text, button in self.button_map.items():
            # Trouver le bouton correspondant dans self.buttons
            button_info = next((btn for btn in self.buttons if btn[0].lower() == text), None)
            
            if button_info:
                _, _, *style, visible = button_info
                # Si le bouton doit être toujours visible, on le rend visible
                if visible:
                    button.setVisible(True)

                else:
                    if len(search_text) > 0:
                        # Sinon, le rendre visible si le texte de recherche correspond
                        button.setVisible(search_text in text.lower())
                    else:
                        button.setVisible(False)

    def sendPrompt(self):

        url = "https://api.openai.com/v1/chat/completions"

        # Créer les en-têtes de la requête
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        }

        # Créer le corps de la requête avec les paramètres nécessaires
        data = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": INIT_PROMPT},
                {"role": "user", "content": self.generate_input.toPlainText()}
            ],
            "max_tokens": 2000  # Optionnel : Limite de tokens pour la réponse
        }

        # Envoyer la requête POST à l'API
        reponse = requests.post(url, headers=headers, data=json.dumps(data))

        # Vérifier si la requête a réussi
        if reponse.status_code == 200:
            # Extraire le texte de la réponse
            completion = reponse.json()
            print(completion['choices'][0]['message']['content'])
            return completion['choices'][0]['message']['content']
        else:
            return None


    def createGraphWithLLM(self):
        self.response_llm = self.sendPrompt()
        if self.response_llm:
            json_graph = json.loads(self.response_llm)["instructions"]
            self.loadFromJSON(json_graph)



    def _create_button_widget(self):

        self.h_layout = QHBoxLayout()
        self.interface_layout = QVBoxLayout()
        self.main_layout.addLayout(self.interface_layout)

        self.h_layout.addWidget(self.graph.widget)
        self.interface_layout.addLayout(self.h_layout)

        # Crée le widget pour contenir le champ de recherche et les boutons
        self.search_and_buttons_widget = QWidget()
        self.search_and_buttons_layout = QVBoxLayout(self.search_and_buttons_widget)
        self.h_layout.addWidget(self.search_and_buttons_widget)
        self.search_and_buttons_widget.setObjectName("searchAndButtonsWidget")

        # Crée et configure le champ de prompt
        buttonGenerate = QPushButton("Generate script")
        self.ai_layout = QVBoxLayout()
        self.generate_input = QTextEdit()
        self.generate_input.setFixedHeight(100)
        self.generate_input.setPlaceholderText("Generate...")
        self.generate_input.textChanged.connect(self.filter_buttons)
        self.generate_input.setObjectName("searchInput")
        self.ai_layout.addWidget(self.generate_input)
        self.ai_layout.addWidget(buttonGenerate)
        self.interface_layout.addLayout(self.ai_layout)
        buttonGenerate.clicked.connect(self.createGraphWithLLM)

        # Crée et configure le champ de recherche
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher...")
        self.search_input.textChanged.connect(self.filter_buttons)
        self.search_input.setObjectName("searchInput")
        self.search_and_buttons_layout.addWidget(self.search_input)

        # Crée un layout pour les boutons hors de l'arbre
        self.top_buttons_layout = QHBoxLayout()
        self.search_and_buttons_layout.addLayout(self.top_buttons_layout)

        # Crée les boutons "execute" et "stop" en dehors de l'arbre
        self.execute_button = QPushButton("execute")
        self.execute_button.setStyleSheet("background-color: rgb(0,255,0);")
        self.execute_button.clicked.connect(self.firstExecution)
        self.top_buttons_layout.addWidget(self.execute_button)

        self.stop_button = QPushButton("stop")
        self.stop_button.setStyleSheet("background-color: rgb(255,0,0);")
        self.stop_button.clicked.connect(self.stopExecution)
        self.top_buttons_layout.addWidget(self.stop_button)

        # Crée le QTreeWidget pour contenir les autres boutons dans une hiérarchie
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderHidden(True)  # Cache l'en-tête du tree view
        self.search_and_buttons_layout.addWidget(self.tree_widget)

        # Ajoute un espace extensible en bas pour pousser les boutons vers le haut
        self.search_and_buttons_layout.addStretch()

        # Définit et ajoute les autres boutons à la mise en page sous des catégories dans l'arbre
        self.buttons = [
            # (nom du boutton, node invoqué, catégorie, visibilité)
            ("Add Move Mouse", lambda: self._create_node('action.MoveMouseNode', 'Move Mouse', 500, 300), "Actions", False),
            ("Add Key", lambda: self._create_node('action.KeyNode', 'Key', 500, 300), "Actions", False),
            ("Add Delay", lambda: self._create_node('control.DelayNode', 'Delay', 500, 300), "Controls", False),
            ("Add Get Image Coord", lambda: self._create_node('action.GetImageCoordNode', 'Get Image Coord', 500, 300), "Actions", False),
            ("Add Search Image Coord", lambda: self._create_node('action.GetSearchedImageCoordNode', 'Search Image Coord', 500, 300), "Actions", False),
            ("Add Click Mouse", lambda: self._create_node('action.ClickMouseNode', 'Click Mouse', 500, 300), "Actions", False),
            ("Add Scroll", lambda: self._create_node('action.ScrollNode', 'Scroll', 500, 300), "Actions", False),
            ("Add Branch", lambda: self._create_node('control.BranchNode', 'Branch to Node', 500, 300).setGraph(self.graph), "Controls", False),
            ("Add For Loop", lambda: self._create_node('control.ForLoopNode', 'For Loop', 500, 300), "Controls", False),
            ("Add For Each Loop", lambda: self._create_node('control.ForEachLoopNode', 'For Each Loop', 500, 300), "Controls", False),
            ("Add Get Cascade Data", lambda: self._create_node('control.GetCascadeDataNode', 'Get Cascade Data', 500, 300), "Controls", False),
            ("Add Float", lambda: self._create_node('data.FloatNode', 'Add float', 500, 300), "Data", False),
            ("Add Float addition", lambda: self._create_node('data.AddFloatNode', 'Float', 500, 300), "Data", False),
            ("Add Array 2D", lambda: self._create_node('data.Array2DNode', 'Array 2D', 500, 300), "Data", False),
            ("Add Array 2D Addition", lambda: self._create_node('data.AddArray2DNode', 'Array 2D addition', 500, 300), "Data", False),
            ("Add Get Copy", lambda: self._create_node('data.GetCopyNode', 'get Copy', 500, 300), "Data", False)
        ]

        # Dictionnaire pour garder la trace des catégories et des boutons
        self.tree_categories = {}
        self.button_map = {}

        for text, method, category, *style, visible in self.buttons:
            # Vérifie si la catégorie existe déjà, sinon la créer
            if category not in self.tree_categories:
                parent_item = QTreeWidgetItem(self.tree_widget)
                parent_item.setText(0, category)
                self.tree_categories[category] = parent_item
            else:
                parent_item = self.tree_categories[category]

            # Crée un bouton comme élément enfant
            button_item = QTreeWidgetItem(parent_item)
            button_widget = QPushButton(text)
            if style:
                button_widget.setStyleSheet(style[0])
            button_widget.clicked.connect(method)
            button_widget.setVisible(visible)  # Visibilité initiale

            # Ajoute le bouton à la map pour une gestion future
            self.tree_widget.setItemWidget(button_item, 0, button_widget)
            self.button_map[text.lower()] = button_widget



    def _create_menu(self):
        menu = self.menuBar().addMenu("File")
        self.menuBar().setStyleSheet("""
            
            QMenuBar::item {
                color: white;   /* Couleur du texte du menu principal */
            }
            QMenuBar::item:selected {
                background-color: #555;
            }
            QMenuBar::item:pressed {
                background-color: #444;
            }
            QMenu::item { 
                color: white;
            }
            QMenu::item:selected {
                color: white;
                background-color: #0078d7;
            }
        """)
        menu.addAction(QAction("Save as...", self, triggered=self.saveToJSON))
        menu.addAction(QAction("Load file", self, triggered=self.readFile))

    def firstExecution(self):
        BotManager.setQueue([])
        self.botManager.addNodeToQueue(self.graph.get_node_by_name('Start'))
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
                QMessageBox.critical(self, "Error", f"Error : {e}")

    def readFile(self):
        # Ouvrir une boîte de dialogue pour choisir l'emplacement et le nom du fichier
        file, _ = QFileDialog.getOpenFileName(self, "Load from a file", "", "JSON file (*.json);;All files (*)")
        if len(file) > 0:
            with open(file, 'r', encoding='utf-8') as file_json:
                data = json.load(file_json)
                self.loadFromJSON(data)

    def loadFromJSON(self, json):

        self.eraseAllNodes()

        # Créer les nodes en fonction des données json
        for node in json:
            node_obj = self.graph.create_node(json[node]["identifier"] + "." + json[node]["type"], name=node, color='#606060')
            node_obj.set_pos(json[node]["coord"]["x"], json[node]["coord"]["y"])
            node_obj.setBotManager(self.botManager)
            node_obj.setGraph(self.graph)

            # Ajout des widgets aux nodes
            if("widgets" in json[node]):
                for widget_name, widget_value in json[node]["widgets"].items():
                    node_obj.get_widget(widget_name).set_value(widget_value)
         
         # Connetc
        for node in json:
            for output in json[node]["outputs"]:
                if len(json[node]["outputs"][output]) > 0:
            
                    node_obj = self.graph.get_node_by_name(node)
                    for i in range(len(json[node]["outputs"][output])):
                        # Récupère dans le graph le node associé au nom donné dans le json et connecte aux autres nodes
                        node_target_obj = self.graph.get_node_by_name(json[node]["outputs"][output][i]["connected node"])
                        input_target = json[node]["outputs"][output][i]["connected input"]
                        output_target_index = self.get_output_index_by_name(node_obj, output)
                        node_obj.set_output(output_target_index, node_target_obj.inputs().get(input_target))

            

    def eraseAllNodes(self):
        # Effacer tous les nodes
        for node in self.graph.all_nodes():
            self.graph.delete_node(node)

    def get_output_index_by_name(self, node, output_name):
        # Prends un node et un string et retourne un output
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


