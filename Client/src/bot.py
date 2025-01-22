from PySide2.QtWidgets import QApplication, QMainWindow, QListWidget, QTabWidget, QLabel, QMenu, QListWidgetItem ,QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QAction, QFileDialog, QMessageBox, QLineEdit, QTextEdit, QTreeWidget, QTreeWidgetItem
from PySide2.QtGui import QKeyEvent
from PySide2.QtCore import Qt
from api_access import create_user, get_token, add_or_update_env_variable, get_api_token_from_env, get_scripts, send_script
from NodeGraphQt import NodeGraph, BaseNode
import json
from node.control.StartNode import StartNode
from node.action.MoveMouseNode import MoveMouseNode
from node.action.KeyNode import KeyNode
from node.control.DelayNode import DelayNode
from node.action.GetImageCoordNode import GetImageCoordNode
from node.action.ClickMouseNode import ClickMouseNode
from node.action.ScrollNode import ScrollNode

from node.control.BranchNode import BranchNode
from node.control.ForLoopNode import ForLoopNode
from node.control.ForEachLoopNode import ForEachLoopNode

from node.action.GetCascadeDataNode import GetCascadeDataNode
from node.data.FloatNode import FloatNode
from node.data.AddFloatNode import AddFloatNode
from node.data.Array2DNode import Array2DNode
from node.data.AddArray2DNode import AddArray2DNode
from node.data.GetCopyNode import GetCopyNode

from node.action.GetSearchedImageCoordNode import GetSearchedImageCoordNode

import threading
import json
import sys
import time
import requests

from dotenv import load_dotenv
import os
from config import INIT_PROMPT


# Manager des nodes, fonctionne comme un interpreter
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
            "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"
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

        self.add_tabs()

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
            ("Add Get Cascade Data", lambda: self._create_node('action.GetCascadeDataNode', 'Get Cascade Data', 500, 300), "Controls", False),
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

    def add_tabs(self):
        # Ajout d'une zone d'onglets
        self.tabs = QTabWidget()
        self.interface_layout.addWidget(self.tabs)

        self.tabs.setFixedHeight(300)

        # Création de l'onglet génération de script avec le contenu demandé
        tab_generate_script = QWidget()
        tab_generate_script_layout = QVBoxLayout(tab_generate_script)

        # Ajout du champ de génération et du bouton dans tab_generate_script
        buttonGenerate = QPushButton("Generate script")
        self.generate_input = QTextEdit()
        self.generate_input.setFixedHeight(100)
        self.generate_input.setPlaceholderText("Generate...")
        self.generate_input.textChanged.connect(self.filter_buttons)
        self.generate_input.setObjectName("searchInput")
        tab_generate_script_layout.addWidget(self.generate_input)
        tab_generate_script_layout.addWidget(buttonGenerate)

        # Connecte le bouton pour appeler createGraphWithLLM
        buttonGenerate.clicked.connect(self.createGraphWithLLM)

        # Ajoute l'onglet Generate script au QTabWidget
        self.tabs.addTab(tab_generate_script, "Generate script")

        env_file_path = '../.env'

        # Recherche du token API
        api_token = get_api_token_from_env(env_file_path)

        # Création de l'onglet Import script
        tab_import_script = QWidget()
        tab_import_script_layout = QVBoxLayout(tab_import_script)
        

        if api_token:
            # Si API_TOKEN est trouvé, afficher la liste avec des exemples
            self.list_widget = QListWidget()
            self.list_widget.setStyleSheet("color: white;")
            tab_import_script_layout.addWidget(self.list_widget)

            # Champ de texte supplémentaire pour entrer un nom de script
            self.script_name_input = QLineEdit()  # Champ de texte pour le nom du script
            self.script_name_input.setPlaceholderText("Enter script name")
            self.script_name_input.setStyleSheet("color: white;")  
            tab_import_script_layout.addWidget(self.script_name_input)

            # Ajouter un bouton d'action pour rafraîchir les scripts
            button_refresh_scripts = QPushButton("Refresh")
            button_refresh_scripts.clicked.connect(self.refresh_scripts)
            tab_import_script_layout.addWidget(button_refresh_scripts)

            # Ajouter un bouton pour ajouter un script
            button_add_script = QPushButton("Add Script")
            button_add_script.clicked.connect(self.send_script_request)
            tab_import_script_layout.addWidget(button_add_script)

            # Initialisation des scripts dès le début
            self.refresh_scripts()

            # Connecter le clic droit à une fonction
            self.list_widget.setContextMenuPolicy(Qt.CustomContextMenu)
            self.list_widget.customContextMenuRequested.connect(self.show_context_menu)

        else:
            # Si le token n'est pas défini, afficher un message
            tab_import_script_layout.addWidget(QLabel("Token non défini"))

        # Ajouter l'onglet à la vue
        self.tabs.addTab(tab_import_script, "Scripts")

    def show_context_menu(self, position):
        """
        Affiche un menu contextuel personnalisé lors d'un clic droit sur un élément de la liste.
        """
        # Crée un menu contextuel
        context_menu = QMenu()

        # Crée une action personnalisée pour le menu contextuel
        action_import = QAction("Import Script", self)
        action_import.triggered.connect(self.import_script)

        # Ajoute l'action au menu contextuel
        context_menu.addAction(action_import)

        # Affiche le menu à la position du clic
        context_menu.exec_(self.list_widget.mapToGlobal(position))

    def import_script(self):
        """
        Fonction appelée lorsque l'utilisateur clique sur 'Import Script' dans le menu contextuel.
        """
        selected_item = self.list_widget.currentItem()
        if selected_item:
            # Récupère les données cachées stockées dans l'item (par exemple, un ID ou un objet JSON)
            hidden_data = selected_item.data(Qt.UserRole)  # Récupère les données cachées
            data = hidden_data.replace('"', '').replace("'", '"')
            self.loadFromJSON(json.loads(data))
            

    def refresh_scripts(self):
        """
        Rafraîchit la liste des scripts depuis l'API et met à jour le QListWidget.
        """
        # Recherche du token API
        api_token = get_api_token_from_env('../.env')

        if api_token:
            try:
                # Récupère les scripts depuis l'API
                list_scripts = get_scripts(api_token, "get-scripts/")

                # Efface les éléments actuels de la liste
                self.list_widget.clear()

                if list_scripts != None:
                    for script in list_scripts["messages"]:
                        # Créer un nouvel item pour chaque script
                        item = QListWidgetItem("script name: "+ str(script["name"]) + ", author:" + str(list_scripts["username"]))

                        # Ajouter des données cachées (par exemple un ID ou un objet JSON) à l'item
                        item.setData(Qt.UserRole, script["content"])  # Ici, on associe un objet JSON
                        self.list_widget.addItem(item)
                else:
                    self.list_widget.addItem("No scripts available.")
            except:
                pass
        else:
            self.list_widget.clear()
            self.list_widget.addItem("Token not defined.")

    def send_script_request(self):
        """
        Envoie un script sélectionné avec un nom de script récupéré depuis le champ de texte.
        """
        # Récupération du token depuis le fichier .env
        token = get_api_token_from_env("../.env")

        # Récupérer le nom du script à partir du champ de texte
        script_name = self.script_name_input.text()

        # Si un nom de script est entré
        if script_name:
            # Récupérer le JSON du graphe et l'envoyer avec le nom
            script_json = self.graphToJson()
            send_script(token, str(script_json), script_name)  # Envoie le script avec le nom
        else:
            print("No script name entered.")

    def _create_menu(self):
        # Menu File
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

        # Menu Settings
        settings_menu = self.menuBar().addMenu("Settings")
        settings_menu.addAction(QAction("Get Token", self, triggered=self.open_get_token_window))


    def open_get_token_window(self):
        self.token_window = TokenWindow(self)
        self.token_window.show()

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

    def graphToJson(self):
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
        
        return data

    def saveToJSON(self):
        data = self.graphToJson()
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


class TokenWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Get Token")
        self.resize(600, 400)

        # Configuration du widget central
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Création des onglets
        self.tabs = QTabWidget(self)
        self._create_tabs()
        layout.addWidget(self.tabs)

    def _create_tabs(self):
        # Onglet 1 : Register
        register_tab = QWidget()
        register_layout = QVBoxLayout(register_tab)

        # Champs pour l'enregistrement
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.first_name_input = QLineEdit()
        self.first_name_input.setPlaceholderText("First Name")
        self.last_name_input = QLineEdit()
        self.last_name_input.setPlaceholderText("Last Name")
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")

        # Bouton pour s'enregistrer
        register_button = QPushButton("Register")
        register_button.clicked.connect(self.register_user)

        # Ajout des widgets au layout
        register_layout.addWidget(self.username_input)
        register_layout.addWidget(self.password_input)
        register_layout.addWidget(self.first_name_input)
        register_layout.addWidget(self.last_name_input)
        register_layout.addWidget(self.email_input)
        register_layout.addWidget(register_button)

        self.tabs.addTab(register_tab, "Register")

        # Onglet 2 : Get Token
        token_tab = QWidget()
        token_layout = QVBoxLayout(token_tab)

        # Champs pour obtenir un token
        self.token_username_input = QLineEdit()
        self.token_username_input.setPlaceholderText("Username")
        self.token_password_input = QLineEdit()
        self.token_password_input.setPlaceholderText("Password")
        self.token_password_input.setEchoMode(QLineEdit.Password)

        # Bouton pour obtenir un token
        token_button = QPushButton("Get Token")
        token_button.clicked.connect(self.get_user_token)

        # Ajout des widgets au layout
        token_layout.addWidget(self.token_username_input)
        token_layout.addWidget(self.token_password_input)
        token_layout.addWidget(token_button)

        self.tabs.addTab(token_tab, "Get new token")

    def register_user(self):
        # Récupération des valeurs
        username = self.username_input.text()
        password = self.password_input.text()
        first_name = self.first_name_input.text()
        last_name = self.last_name_input.text()
        email = self.email_input.text()

        # Appel de la fonction d'enregistrement
        response = create_user(username, password, first_name, last_name, email)

        if response.status_code == 201:
            QMessageBox.information(self, "Success", "User registered successfully!")
        else:
            QMessageBox.critical(self, "Error", f"Failed to register user: {response.json()}")

    def get_user_token(self):
        # Récupération des valeurs
        username = self.token_username_input.text()
        password = self.token_password_input.text()

        # Appel de la fonction pour obtenir un token
        response = get_token(username, password)
        

        if response is None:
            QMessageBox.critical(self, "Error", "Failed to connect to the server.")
            return

        if response.status_code == 200:
            # Extraire le token depuis la réponse JSON
            try:
                token = response.json().get("token")
                if token:
                    QMessageBox.information(self, "Token Retrieved", f"Token: {token}")
                    add_or_update_env_variable("../.env", "API_TOKEN", token)
                else:
                    QMessageBox.critical(self, "Error", "Token not found in response.")
            except ValueError:
                QMessageBox.critical(self, "Error", "Failed to parse server response.")
        else:
            # Extraire un message d'erreur ou afficher une erreur générique
            error_message = response.json().get("message", "Unknown error")
            QMessageBox.critical(self, "Error", f"Failed to get token: {error_message}")




if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Créer et afficher la fenêtre principale
    main_window = MainWindow()
    main_window.show()

    sys.exit(app.exec_())


