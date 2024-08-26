from node.Node import Node
import pyautogui


class ClickMouseNode(Node):
    __identifier__ = 'action'  # Identifiant du noeud
    NODE_NAME = 'ClickMouseNode'       # Nom du noeud

    def __init__(self):
        super(ClickMouseNode, self).__init__()

        # Ajout de ports d'entrée et de sortie
        self.add_input('input')
        self.add_output('output')
        
        items = ['right', 'left']
        self.add_combo_menu('click', 'click', items)

    def action(self):
        print("execution click")
        pyautogui.click(button=self.get_property('click'))