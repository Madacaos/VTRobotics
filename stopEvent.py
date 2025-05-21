from event import Event

class StopEvent(Event):
    def __init__(self, robotics):
        # Usa super con la classe SpeechEvent
        Event.__init__(self, robotics)  # Chiamata diretta al costruttore della classe base