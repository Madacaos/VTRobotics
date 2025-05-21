from event import Event

class SpeechEvent(Event):
    def __init__(self, robotics, text):
        # Usa super con la classe SpeechEvent
        Event.__init__(self, robotics)  # Chiamata diretta al costruttore della classe base
        self.text = text