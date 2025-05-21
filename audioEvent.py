from event import Event

class AudioEvent(Event):
    def __init__(self, robotics, duration):
        # Usa super con la classe SpeechEvent
        Event.__init__(self, robotics)  # Chiamata diretta al costruttore della classe base
        self.duration = duration
