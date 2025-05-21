import socket
import traceback
import os

class Network:
    @staticmethod
    def get_local_ip():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0)
        try:
            s.connect(('10.254.254.254', 1))
            ip = s.getsockname()[0]
        except Exception:
            Logger.log("Questo dispositivo non possiede un ip locale valido. Verifica configurazioni DHCP.", LogType.ERRORE)
            ip = "127.0.0.1"
        finally:
            s.close()
        return ip

class Logger:
    COLOR = {
        "INFO": "\033[0m",
        "DEBUG": "\033[0;34m",
        "WARNING": "\033[93m",
        "ERRORE": "\033[91m"
    }

    @staticmethod
    def log(message, log_type="INFO", stripped = True):
        # Strip linee e spazi messaggi
        if stripped:
            message = message.strip()

        # Ottieni il nome del file e il numero di riga
        file_name, line_number = traceback.extract_stack()[-2][:2]
        file_name = os.path.basename(file_name)

        # Suddividi il messaggio in righe
        message_lines = message.splitlines()

        # Costruisci e stampa ogni riga con l'header
        for line in message_lines:
            if stripped:
                line = line.strip()
            print("{}[{}:{}] {}{}".format(
                Logger.COLOR.get(log_type, "\033[0m"), file_name, line_number, line, "\033[0m"
            ))

class LogType(type):
    INFO = "INFO"
    WARNING = "WARNING"
    ERRORE = "ERRORE"
    DEBUG = "DEBUG"