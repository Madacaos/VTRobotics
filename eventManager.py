import inspect
import threading

from utils import Logger, LogType
from inspect import getmembers, ismethod, getargspec

class EventManager:
    def __init__(self):
        self.listeners = []
        Logger.log("EventManager inizializzato con successo.")

    def addListener(self, listener):
        self.listeners.append(listener)

    def syncSendEvent(self, event):
        event_name = event.__class__.__name__
        Logger.log("Invio di {} ai listeners...".format(event_name), LogType.DEBUG)

        for listener in self.listeners:
            methods = getmembers(listener, ismethod)  # Ottieni i metodi del listener

            for method_name, method in methods:
                try:
                    # Ottieni gli argomenti del metodo
                    argspec = getargspec(method)
                    param_names = [arg.lower() for arg in argspec.args if arg != "self"]

                    # Controlla se il nome dell'evento e' negli argomenti
                    if event_name.lower() not in param_names:
                        continue

                    # Chiama il metodo con l'evento
                    method.__call__(event)
                    Logger.log("Evento '{}' inviato alla classe '{}', metodo: '{}'".format(
                        event_name, listener.__class__.__name__, method_name), LogType.DEBUG)

                except Exception as e:
                    Logger.log("Errore durante l'invio dell'evento a '{}', metodo: '{}'. Dettagli: {}".format(
                        listener.__class__.__name__, method_name, str(e)), LogType.ERRORE)

    def sendEvent(self, event):
        event_name = event.__class__.__name__
        Logger.log("Invio di {} ai listeners...".format(event_name), LogType.DEBUG)

        for listener in self.listeners:
            methods = getmembers(listener, ismethod)  # Ottieni i metodi del listener

            for method_name, method in methods:
                try:
                    # Ottieni gli argomenti del metodo
                    argspec = getargspec(method)
                    param_names = [arg.lower() for arg in argspec.args if arg != "self"]

                    # Controlla se il nome dell'evento e' negli argomenti
                    if event_name.lower() not in param_names:
                        continue

                    # Chiama il metodo con l'evento
                    threading.Thread(target=method, args=(event,)).start()
                    Logger.log("Evento '{}' inviato alla classe '{}', metodo: '{}'".format(
                        event_name, listener.__class__.__name__, method_name), LogType.DEBUG)

                except Exception as e:
                    Logger.log("Errore durante l'invio dell'evento a '{}', metodo: '{}'. Dettagli: {}".format(
                        listener.__class__.__name__, method_name, str(e)), LogType.ERRORE)