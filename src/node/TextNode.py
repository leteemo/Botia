from node.Node import Node
import pyautogui

class TextNode(Node):
    __identifier__ = 'action'
    NODE_NAME = 'TextNode'

    def __init__(self):
        super(TextNode, self).__init__()
        
        self.add_input('input')
        self.add_output('output')
        
        # Texte à écrire
        self.add_text_input('key', label='Text to write', tooltip="Texte à taper dans l’input")

        # Intervalle entre chaque caractère
        self.add_text_input('interval', label='Delay (s)', text="0.05", tooltip="Délai entre chaque caractère (ex: 0.05)")

    def action(self):
        text = self.get_property('key') or ""

        # Récupère la valeur de l'intervalle, convertie en float, avec fallback
        interval_str = self.get_property('interval')
        try:
            interval = float(interval_str)
        except (TypeError, ValueError):
            interval = 0.05  # Valeur par défaut

        print(f"Exécution de l’écriture : \"{text}\" avec intervalle de {interval}s")
        pyautogui.write(text, interval=interval)