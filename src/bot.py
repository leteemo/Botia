from PySide2.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QAction, QFileDialog, QMessageBox, QLineEdit, QTextEdit, QTreeWidget, QTreeWidgetItem
from PySide2.QtGui import QKeyEvent
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QDialog, QLabel
from NodeGraphQt import NodeGraph, BaseNode

from node.StartNode import StartNode
from node.MoveMouseNode import MoveMouseNode
from node.KeyNode import KeyNode
from node.TextNode import TextNode
from node.DelayNode import DelayNode
from node.GetImageCoordNode import GetImageCoordNode
from node.ClickMouseNode import ClickMouseNode
from node.ScrollNode import ScrollNode

from node.data.EqualNode import EqualNode
from node.BranchNode import BranchNode
from node.ForLoopNode import ForLoopNode
from node.ForEachLoopNode import ForEachLoopNode
from node.GetAIObjectCoordNode import GetAIObjectCoordNode
from node.IfNode import IfNode
from node.GetCascadeDataNode import GetCascadeDataNode
from node.data.FloatNode import FloatNode
from node.data.AddFloatNode import AddFloatNode
from node.data.Array2DNode import Array2DNode
from node.data.AddArray2DNode import AddArray2DNode
from node.data.GetCopyNode import GetCopyNode

from node.GetImageFromSearch import GetImageFromSearch

import threading
import json
import sys
import time
import requests

from config import INIT_PROMPT
import os

from PySide2.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QComboBox, QLineEdit, QWidget, QFormLayout
)

from PySide2.QtCore import QSettings



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

        self.settings_window = None

        self.config = ConfigManager()
        settings = self.config.load()  # Renvoie dict avec defaults si vide

        self.api_choice = settings.get("api_choice", "gpt")
        self.model = settings.get("model", "")
        self.url = settings.get("url", "")

        

    def save_and_close(self):
        self.config.save(
            self.api_choice.currentText(),
            self.model_input.text(),
            self.url_input.text()
        )
        self.close()

    def openSettingsWindow(self):
        self.settings_window = SettingsWindow(self)
        self.settings_window.show()

    def updateSettingsFromWindow(self):
        if self.settings_window:
            settings = self.settings_window.get_settings()
            self.config.save(settings["api_choice"], settings["model"], settings["url"])
            self.settings = settings
            print("Settings mises à jour :", self.settings)

    def openSettingsWindow(self):
        if self.settings_window is None:
            self.settings_window = SettingsWindow(self)
        self.settings_window.show()


    # Enregistrement des nodes dans le graphe
    def _register_nodes(self):
        nodes = [StartNode, MoveMouseNode, KeyNode, TextNode, DelayNode, GetImageCoordNode, GetAIObjectCoordNode, IfNode, ClickMouseNode, ScrollNode, GetImageFromSearch,
            BranchNode, ForLoopNode, ForEachLoopNode, GetCascadeDataNode, FloatNode, EqualNode, AddFloatNode, Array2DNode, AddArray2DNode, GetCopyNode]
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

        for category, parent_item in self.tree_categories.items():
            show_category = False  # On cache par défaut

            for i in range(parent_item.childCount()):
                child_item = parent_item.child(i)
                button = self.tree_widget.itemWidget(child_item, 0)
                button_text = button.text().lower()

                # Trouver le bouton d’origine
                button_info = next((btn for btn in self.buttons if btn[0].lower() == button_text), None)
                always_visible = button_info[4] if button_info else False

                # Afficher si texte vide ou correspondance
                if always_visible or (search_text in button_text):
                    button.setVisible(True)
                    child_item.setHidden(False)  # Important : afficher l’item dans le QTree
                    show_category = True
                else:
                    button.setVisible(False)
                    child_item.setHidden(True)  # Cacher l’item du QTree

            # Cacher ou montrer la catégorie
            parent_item.setHidden(not show_category)

            # Gestion de l'expansion selon présence recherche
            if show_category:
                if search_text:
                    self.tree_widget.expandItem(parent_item)
                else:
                    # Si pas de recherche, garder minimisé
                    self.tree_widget.collapseItem(parent_item)
            else:
                self.tree_widget.collapseItem(parent_item)







    def sendPromptOpenAI(self):

        url = self.url
        api_key = os.getenv("OPENAI_API_KEY")

        # Créer les en-têtes de la requête
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        # Créer le corps de la requête avec les paramètres nécessaires
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": INIT_PROMPT},
                {"role": "user", "content": self.generate_input.toPlainText()}
            ]
        }

        # Envoyer la requête POST à l'API
        response = requests.post(url, headers=headers, data=json.dumps(data))

        # Vérifier si la requête a réussi
        if response.status_code == 200:
            # Extraire le texte de la réponse
            completion = response.json()
            print(completion['choices'][0]['message']['content'])
            return completion['choices'][0]['message']['content']
        else:
            return None


    def sendPromptOllama(self):

        api_key = os.getenv("OPENAI_API_KEY")
        model = self.model
        url = self.url
        

        headers = {
            "Content-Type": "application/json"
        }

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": INIT_PROMPT},
                {"role": "user", "content": self.generate_input.toPlainText()}
            ],
            "stream": False
        }


        response = requests.post(url, headers=headers, data=json.dumps(payload))
        # Vérifier si la requête a réussi
        if response.status_code == 200:
            # Extraire le texte de la réponse
            completion = response.json()
            print(completion["choices"][0]["message"]["content"])
            return completion["choices"][0]["message"]["content"]
        else:
            return None


    def createGraphWithLLM(self):
        
        if self.settings_window and self.settings_window.isVisible():
            settings = self.settings_window.get_settings()
            self.api_choice = settings["api_choice"]
            self.model = settings["model"]
            self.url = settings["url"]

        else:
            # Utiliser les settings déjà chargés au lancement
            pass

        if self.api_choice == "ollama":
            self.response_llm = self.sendPromptOllama()
        elif self.api_choice == "gpt":
            self.response_llm = self.sendPromptOpenAI()
        
        if self.response_llm:
            json_graph = json.loads(self.response_llm)["instructions"]
            self.loadFromJSON(json_graph)

    def getSettingsFromWindow(self):
        if hasattr(self, 'settings_window'):
            return self.settings_window.get_settings()
        else:
            print("Settings window not open")
            return None



    def _create_button_widget(self):
        # Layout principal horizontal
        self.h_layout = QHBoxLayout()
        self.main_layout.addLayout(self.h_layout)

        # À gauche, on met le graph.widget, qui prend tout l'espace possible
        self.h_layout.addWidget(self.graph.widget, 1)  # 1 = stretch

        # À droite, un widget contenant la zone recherche + boutons
        self.right_widget = QWidget()
        self.right_widget.setObjectName("searchAndButtonsWidget")
        self.h_layout.addWidget(self.right_widget)
        self.h_layout.setStretchFactor(self.right_widget, 0)

        # Layout vertical pour la zone droite
        self.right_layout = QVBoxLayout(self.right_widget)
        self.right_layout.setContentsMargins(0, 0, 0, 0)
        self.right_layout.setSpacing(5)

        # Champ de recherche (en haut)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher...")
        self.search_input.textChanged.connect(self.filter_buttons)
        self.search_input.setObjectName("searchInput")
        self.right_layout.addWidget(self.search_input)

        # Boutons Execute / Stop (juste en dessous du champ recherche)
        self.top_buttons_layout = QHBoxLayout()
        self.execute_button = QPushButton("execute")
        self.execute_button.setStyleSheet("background-color: rgb(0,180,0);")
        self.execute_button.clicked.connect(self.firstExecution)
        self.top_buttons_layout.addWidget(self.execute_button)

        self.stop_button = QPushButton("stop")
        self.stop_button.setStyleSheet("background-color: rgb(180,0,0);")
        self.stop_button.clicked.connect(self.stopExecution)
        self.top_buttons_layout.addWidget(self.stop_button)

        self.right_layout.addLayout(self.top_buttons_layout)

        # Tree widget pour les boutons, prend tout l'espace restant
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderHidden(True)
        self.right_layout.addWidget(self.tree_widget, 1)  # Stretch 1 = prend tout

        # Espace extensible entre tree_widget et prompt/bouton
        # (pour pousser le prompt en bas)
        # En fait on a déjà stretch 1 sur tree_widget, donc pas besoin de addStretch()

        # Zone prompt + bouton Generate (toujours en bas)
        self.ai_widget = QWidget()
        self.ai_layout = QVBoxLayout(self.ai_widget)
        self.ai_layout.setContentsMargins(0, 0, 0, 0)
        self.ai_layout.setSpacing(5)

        self.generate_input = QTextEdit()
        self.generate_input.setFixedHeight(200)
        self.generate_input.setPlaceholderText("Ask to AI to generate a script...")
        self.generate_input.textChanged.connect(self.filter_buttons)
        self.generate_input.setObjectName("searchInput")
        self.ai_layout.addWidget(self.generate_input)

        buttonGenerate = QPushButton("Generate script")
        buttonGenerate.clicked.connect(self.createGraphWithLLM)
        self.ai_layout.addWidget(buttonGenerate)

        self.right_layout.addWidget(self.ai_widget)

        # --- Initialisation des boutons dans l'arbre ---
        self.buttons = [
            # (nom, méthode, catégorie, style, visible)
            ("Add Move Mouse", lambda: self._create_node('action.MoveMouseNode', 'Move Mouse', 500, 300), "Actions", "", False),
            ("Add Key", lambda: self._create_node('action.KeyNode', 'Key', 500, 300), "Actions", "", False),
            ("Add Text", lambda: self._create_node('action.TextNode', 'Key', 500, 300), "Actions", "", False),
            ("Add Get Cascade Data", lambda: self._create_node('control.GetCascadeDataNode', 'Get Cascade Data', 500, 300), "Actions", "", False),
            ("Add Delay", lambda: self._create_node('control.DelayNode', 'Delay', 500, 300), "Controls", "", False),
            ("Add If", lambda: self._create_node('control.IfNode', 'If', 500, 300), "Controls", "", False),
            ("Add Get Image Coord", lambda: self._create_node('action.GetImageCoordNode', 'Get Image Coord', 500, 300), "Actions", "", False),
            ("Add Get Object Coord With AI", lambda: self._create_node('action.GetAIObjectCoordNode', 'Get Object Coord with Ai', 500, 300), "Actions", "", False),
            ("Add Search Image Coord", lambda: self._create_node('action.GetImageFromSearch', 'Search Image Coord', 500, 300), "Actions", "", False),
            ("Add Click Mouse", lambda: self._create_node('action.ClickMouseNode', 'Click Mouse', 500, 300), "Actions", "", False),
            ("Add Scroll", lambda: self._create_node('action.ScrollNode', 'Scroll', 500, 300), "Actions", "", False),
            ("Add Branch", lambda: self._create_node('control.BranchNode', 'Branch to Node', 500, 300).setGraph(self.graph), "Controls", "", False),
            ("Add For Loop", lambda: self._create_node('control.ForLoopNode', 'For Loop', 500, 300), "Controls", "", False),
            ("Add For Each Loop", lambda: self._create_node('control.ForEachLoopNode', 'For Each Loop', 500, 300), "Controls", "", False),
            ("Add Equal", lambda: self._create_node('data.EqualNode', 'Equal', 500, 300), "Data", "", False),
            ("Add Float", lambda: self._create_node('data.FloatNode', 'Float', 500, 300), "Data", "", False),
            ("Add Float addition", lambda: self._create_node('data.AddFloatNode', 'Float Addition', 500, 300), "Data", "", False),
            ("Add Array 2D", lambda: self._create_node('data.Array2DNode', 'Array 2D', 500, 300), "Data", "", False),
            ("Add Array 2D Addition", lambda: self._create_node('data.AddArray2DNode', 'Array 2D addition', 500, 300), "Data", "", False),
            ("Add Get Copy", lambda: self._create_node('data.GetCopyNode', 'get Copy', 500, 300), "Data", "", False)
        ]

        self.tree_categories = {}
        self.button_map = {}

        for text, method, category, style, visible in self.buttons:
            # Vérifie si la catégorie existe déjà, sinon la créer
            if category not in self.tree_categories:
                parent_item = QTreeWidgetItem(self.tree_widget)
                parent_item.setText(0, category)
                self.tree_categories[category] = parent_item
                
                # Réduire la catégorie par défaut
                self.tree_widget.collapseItem(parent_item)
            else:
                parent_item = self.tree_categories[category]

            # Crée un bouton comme élément enfant
            button_item = QTreeWidgetItem(parent_item)
            button_widget = QPushButton(text)

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
        
        settings_menu = self.menuBar().addMenu("Settings")
        action_settings = QAction("Open Settings", self)
        action_settings.triggered.connect(self.openSettingsWindow)
        settings_menu.addAction(action_settings)


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



class SettingsWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.resize(400, 250)

        self.settings = QSettings("MonApp", "Botia")  # Nom organisation/app

        layout = QVBoxLayout()
        form_layout = QFormLayout()

        self.api_choice = QComboBox()
        self.api_choice.addItems(["gpt", "ollama"])
        form_layout.addRow(QLabel("API Choice:"), self.api_choice)

        self.model_input = QLineEdit()
        self.model_input.setPlaceholderText("Enter model name")
        form_layout.addRow(QLabel("Model:"), self.model_input)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter URL")
        form_layout.addRow(QLabel("URL:"), self.url_input)

        layout.addLayout(form_layout)

        close_btn = QPushButton("Save & Close")
        close_btn.clicked.connect(self.save_and_close)
        layout.addWidget(close_btn)

        self.setLayout(layout)

        # Charger les valeurs enregistrées au lancement
        self.load_settings()

        # Style pour texte blanc et fond sombre (optionnel)
        self.setStyleSheet("""
            QLabel, QLineEdit, QComboBox, QPushButton {
                color: white;
                background-color: #2b2b2b;
            }
            QLineEdit, QComboBox {
                border: 1px solid #555;
                padding: 4px;
                border-radius: 3px;
            }
            QPushButton {
                background-color: #444;
                border: none;
                padding: 6px 12px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #666;
            }
        """)

    def load_settings(self):
        self.api_choice.setCurrentText(self.settings.value("api_choice", "gpt"))
        self.model_input.setText(self.settings.value("model", ""))
        self.url_input.setText(self.settings.value("url", ""))

    def save_settings(self):
        self.settings.setValue("api_choice", self.api_choice.currentText())
        self.settings.setValue("model", self.model_input.text())
        self.settings.setValue("url", self.url_input.text())

    def save_and_close(self):
        self.save_settings()
        self.close()

    def get_settings(self):
        return {
            "api_choice": self.api_choice.currentText(),
            "model": self.model_input.text(),
            "url": self.url_input.text()
        }

class ConfigManager:
    def __init__(self):
        self.settings = QSettings("MonApp", "Botia")

    def load(self):
        return {
            "api_choice": self.settings.value("api_choice", "gpt"),
            "model": self.settings.value("model", ""),
            "url": self.settings.value("url", "")
        }

    def save(self, api_choice, model, url):
        self.settings.setValue("api_choice", api_choice)
        self.settings.setValue("model", model)
        self.settings.setValue("url", url)

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Créer et afficher la fenêtre principale
    main_window = MainWindow()
    main_window.show()

    sys.exit(app.exec_())


