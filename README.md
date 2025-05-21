# VTRobotics

## Descrizione

VTRobotics è un framework sviluppato dagli studenti dell'Istituto Verona Trento per l'interazione con robot umanoidi NAO. Il sistema integra riconoscimento vocale, sintesi vocale, gestione dei movimenti e intelligenza artificiale per creare un'esperienza interattiva completa.

Una delle sfide più importanti è stato rendere di facile comprensione e di sostenibile convenienza l'organizzazione interna del codice di Nao. Allo stato attuale Aldebaran fornisce librerie di interfaccia verso ogni componente fisico, ma per organizzare un team di studenti vasto necessitavamo di una maggiore organizzazione che partisse dal riorganizzamento della logica stessa del progetto.

Al tal fine è stato sviluppato questo framework in grado di semplificare le più consuete task svolte dal nostro robot, permettendo di gestire ogni componentistica con un paradigma strutturale orientato verso l'uso di classi ed oggetti.

## Architettura del Sistema

Il sistema è basato su un'architettura modulare event-driven, dove i diversi componenti comunicano attraverso un sistema di eventi. La classe principale `Robotics` inizializza e coordina tutti i moduli del sistema.

```python
# robotics.py - Classe principale che inizializza tutti i componenti
class Robotics:
    def __init__(self):
        Logger.log("""    
             __      __                     _______             _        
             \ \    / /                    |__   __|           | |       
              \ \  / /__ _ __ ___  _ __   __ _| |_ __ ___ _ __ | |_ ___  
               \ \/ / _ \ '__/ _ \| '_ \ / _` | | '__/ _ \ '_ \| __/ _ \ 
                \  /  __/ | | (_) | | | | (_| | | | |  __/ | | | || (_) |
                 \/ \___|_|  \___/|_| |_|\__,_|_|_|  \___|_| |_|\__\___/ 
                          _____       _           _   
                         |  __ \     | |         | | (_)         
                         | |__) |___ | |__   ___ | |_ _  ___ ___ 
                         |  _  // _ \| '_ \ / _ \| __| |/ __/ __|
                         | | \ \ (_) | |_) | (_) | |_| | (__\__ \\
                         |_|  \_\___/|_.__/ \___/ \__|_|\___|___/

                 Questo programma e\' frutto di continue ricerche e lavoro svolto
                sinergeticamente dagli ex studenti del VeronaTrento, sentiti libero
                 di applicare modifiche in futuro per migliorarne il funzionamento

                        - Mirko Cerasi (https://github.com/Madacaos)
                """, stripped=False)

    def start(self):
        self.threads = []

        self.proxy = Proxy(robotics=self)
        self.eventManager = EventManager()

        # Inizializzazione dei moduli
        self.voiceManager = VoiceManager(self)
        self.motionManager = MotionManager(self)
        
        # Inizializzazione del broker Python per NAOqi
        try:
            self.pythonBroker = ALBroker("pythonBroker", self.proxy.ip, 0, self.proxy.ip, self.proxy.port)
            self.audioCapture = AudioCaptureModule("AudioCapture", self)
            self.audioCapture.calibrate_activation_threshold()
        except RuntimeError as e:
            print("Error initializing broker! ", e)
            traceback.print_exc()
            exit(1)
        self.chatAssistant = ChatAssistant(self)
```

### Componenti Principali

#### Sistema di Listeners (EventManager)

È stato creato un sistema di Listeners in grado di gestire una mole non indifferente di eventi, evocabili su thread separati, permettendo di gestire la logica delle situazioni in cui NAO è posto, in modo efficace ed intuitivo.

```python
# eventManager.py - Gestione degli eventi e dei listeners
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

                    # Controlla se il nome dell'evento è negli argomenti
                    if event_name.lower() not in param_names:
                        continue

                    # Chiama il metodo con l'evento
                    method.__call__(event)
                    Logger.log("Evento '{}' inviato alla classe '{}', metodo: '{}'".format(
                        event_name, listener.__class__.__name__, method_name), LogType.DEBUG)

                except Exception as e:
                    Logger.log("Errore durante l'invio dell'evento a '{}', metodo: '{}'. Dettagli: {}".format(
                        listener.__class__.__name__, method_name, str(e)), LogType.ERRORE)
```

Esempio di creazione e utilizzo di un evento:

```python
# Definizione di un evento
class SpeechEvent(Event):
    def __init__(self, robotics, text):
        Event.__init__(self, robotics)  # Chiamata al costruttore della classe base
        self.text = text

# Invio di un evento
self.eventManager.sendEvent(SpeechEvent(self, "Ciao, come stai?"))

# Creazione di un listener che risponde all'evento
class MyListener:
    def onSpeech(self, speechEvent):
        print("Ho ricevuto un evento di tipo Speech con testo: " + speechEvent.text)
        # Esegui azioni in risposta all'evento

# Registrazione del listener
eventManager.addListener(MyListener())
```

#### Proxy Manager

Ogni connessione con le API di NAO viene memorizzata all'interno del nostro proxy manager al fine di garantire una riduzione del carico di rete ed aprendo uniche interfacce per periferica richiesta nel tempo.

```python
# proxy.py - Gestione delle connessioni ai servizi NAOqi
class Proxy():
    def __init__(self, robotics, ip = Network.get_local_ip(), port = 9559):
        self.ip = ip
        self.port = port
        self.robotics = robotics

        try:
            self.session = qi.Session()
            self.session.connect("tcp://"+ ip + ":" + str(port))

            # Inizializzazione dei servizi NAOqi
            self.animatedSpeech = self.session.service("ALAnimatedSpeech")
            self.posture = self.session.service("ALRobotPosture")
            self.speech = self.session.service("ALTextToSpeech")
            self.audioPlayer = self.session.service("ALAudioPlayer")
            self.memory = self.session.service("ALMemory")
            self.leds = self.session.service("ALLeds")
            self.audioDevice = self.session.service("ALAudioDevice")

        except Exception as e:
            Logger.log("Errore critico, non e\' stato possibile connettersi a NaoQI. " + str(e), LogType.ERRORE)
            return
        Logger.log("Proxy avviato sull\'ip "+ip+":"+str(port))
```

Esempio di utilizzo del Proxy per controllare il robot:

```python
# Esempio di utilizzo del proxy per far parlare il robot
self.robotics.proxy.speech.say("Ciao, sono NAO!")

# Esempio di utilizzo del proxy per cambiare postura
self.robotics.proxy.posture.goToPosture("Stand", 1.0)

# Esempio di utilizzo del proxy per controllare i LED
self.robotics.proxy.leds.fadeRGB("FaceLeds", 1, 0, 0, 0.5)  # LED rossi
```

#### Sistema di Riconoscimento Vocale

Aldebaran fornisce un sistema proprietario di riconoscimento vocale, che spesso commette errori nella trascrizione vocale del testo. Per questo motivo lo abbiamo rivisitato, creando un nuovo sistema di riconoscimento vocale, in grado di riconoscere i momenti di picco (decibel) ambientali e di registrare le voci. Tali registrazioni vengono condivise con le API di Google al fine di ottenere una trascrizione affidabile e chiara di quanto è stato detto durante la fase di ascolto.

```python
# audioCapture.py - Sistema di riconoscimento vocale avanzato
class AudioCaptureModule(object):
    def __init__(self, name, robotics):
        super(AudioCaptureModule, self).__init__()

        # Connessione al robot
        connection_url = "tcp://" + robotics.proxy.ip + ":" + str(robotics.proxy.port)
        app = qi.Application(["AudioCaptureModule", "--qi-url=" + connection_url])
        robotics.proxy.session.registerService("AudioCaptureModule", self)
        app.start()

        # Inizializzazione del dispositivo audio
        self.audio_device = robotics.proxy.audioDevice
        self.audio_device.enableEnergyComputation()
        self.is_listening = False
        self.is_speech = False
        self.audio_device.subscribe("AudioCaptureModule")

        # Configurazione del riconoscimento vocale
        self.activation_threshold = 0
        self.robotics = robotics
        self.recognizer = sr.Recognizer()
        self.calibration_time = 1

        self.buffer = []
        self.calibrate_activation_threshold()
        self.start_listening()

        # Registrazione come listener per gli eventi
        self.robotics.eventManager.addListener(self)

        # Avvio del thread di controllo
        thread = threading.Thread(target=self.checkTask)
        self.robotics.threads.append(thread)
        thread.start()
```

Il sistema elimina la necessità di parole di attivazione specifiche: NAO rimane costantemente in ascolto, identificando autonomamente quando viene interpellato grazie a un sistema di riconoscimento contestuale avanzato.

```python
# Esempio di elaborazione del buffer audio e riconoscimento vocale
def process_audio_buffer(self, buffer):
    # Conversione del buffer in un formato compatibile con SpeechRecognition
    audio_data = self.convert_buffer_to_audio_data(buffer)
    
    try:
        # Utilizzo delle API Google per il riconoscimento vocale
        text = self.recognizer.recognize_google(audio_data, language="it-IT")
        Logger.log("Testo riconosciuto: " + text)
        
        # Invio dell'evento di riconoscimento vocale
        self.robotics.eventManager.sendEvent(SpeechEvent(self.robotics, text))
    except sr.UnknownValueError:
        Logger.log("Google Speech Recognition non ha capito l'audio", LogType.WARNING)
    except sr.RequestError as e:
        Logger.log("Impossibile richiedere risultati da Google Speech Recognition; {0}".format(e), LogType.ERRORE)
```

#### Sistema TTS (Text-to-Speech)

Per quanto efficace, la voce attualmente adottata dal modulo italiano equipaggiato nei NAO risulta troppo robotica ed alle volte incorre in errori di dettatura. Per questo motivo anche tale sistema è stato ampliato in qualcosa di più grande ed affidabile. Adottiamo un sistema TTS ospitato presso il server ubicato nel nostro istituto al fine di demandare compiti di dettatura complessi verso macchine performanti.

```python
# voiceManager.py - Sistema TTS personalizzato
class VoiceManager:
    def __init__(self, robotics):
        self.server_ip = "your-ip-tts-here"
        self.server_port = "your-port-here"
        self.server_secret = "your-secret-token-here"
        self.server_headers = {
            'Content-Type': 'application/json',
        }

        self.path = os.path.dirname(os.path.abspath(__file__))

        self.robotics = robotics
        self.queue = []

        self.robotics.eventManager.addListener(self)

        thread = threading.Thread(target=self.task)
        robotics.threads.append(thread)
        thread.start()

    def tts(self, text):
        response = requests.post(
                        "http://{}:{}/tts".format(self.server_ip, self.server_port),
                        headers=self.server_headers,
                        data=json.dumps({
                            "secret": self.server_secret,
                            "text": text
                        })
        )

        with open("voice.ogg", "wb") as f:
            f.write(response.content)
```

La nostra nuova voce rappresenta un nuovo look iconico, capace di farci distinguere proprio come le caratteristiche che le voci umane dovrebbero avere.

```python
# Esempio di utilizzo del VoiceManager
# Far parlare il robot con la voce personalizzata
self.robotics.voiceManager.say("Ciao, sono NAO e utilizzo una voce personalizzata di alta qualità!")

# Gestione della sincronizzazione tra audio e movimenti
def onAudio(self, audioEvent):
    timeEnd = time.time() * 1000 + (audioEvent.duration * 1000)

    while(time.time() * 1000 < timeEnd):
        self.robotics.motionManager.playGesture(TalkGesture.random())
        sleep(2)
```

#### Gestione dei Movimenti

Il `MotionManager` controlla i movimenti e le posture del robot, sincronizzandoli con il parlato per creare un'esperienza più naturale.

```python
# motionManager.py - Gestione dei movimenti e delle posture
class MotionManager:
    def __init__(self, robotics):
        self.robotics = robotics
        self.queue = []
        thread = threading.Thread(target=self.task)
        robotics.threads.append(thread)
        thread.start()

    def playGesture(self, gesture, priority = 0):
        self.queue.append(Motion("animations/Stand/Gestures/" + gesture, priority, MotionType.GESTURE))

    def playPosture(self, posture, priority = 0):
        self.queue.append(Motion(posture, priority, MotionType.POSTURE))

    def next(self):
        priority = 0
        index = 0

        # Seleziona il movimento con priorità più alta
        for i in range(len(self.queue)):
            motion = self.queue[i]
            if motion.priority > priority:
                index = i
                priority = motion.priority

        motion = self.queue[index]
        self.queue.pop(index)
        
        # Esegue il movimento appropriato
        if motion.motionType == MotionType.POSTURE:
            self.robotics.proxy.posture.goToPosture(motion.animation, 1.0)
        else:
            self.robotics.proxy.animatedSpeech.say("^run(animations/Stand/Gestures/" + motion.animation + ")")
```

Esempio di utilizzo del MotionManager:

```python
# Eseguire un gesto predefinito
self.robotics.motionManager.playGesture(TalkGesture.EXPLAIN1)

# Cambiare postura
self.robotics.motionManager.playPosture("Stand", 1)  # Priorità 1

# Eseguire un gesto casuale durante il parlato
self.robotics.motionManager.playGesture(TalkGesture.random())
```

#### Integrazione con Intelligenza Artificiale

Il `ChatAssistant` integra un'intelligenza artificiale per la conversazione, comunicando con un server AI esterno.

```python
# chatAssistant.py - Integrazione con AI per la conversazione
class ChatAssistant:
    def __init__(self, robotics):
        self.server_ip = "your-ip-here"
        self.server_port = "your-port-here"
        self.server_url = "http://{}:{}".format(self.server_ip, self.server_port)
        self.server_secret = "your-secret-token-here"

        self.server_headers = {
            'Content-Type': 'application/json',
        }

        self.robotics = robotics
        robotics.eventManager.addListener(self)
        self.create_chat("default-comparellobello")

    def ask(self, text):
        response = requests.post(self.server_url + "/sendMessage", headers=self.server_headers,
                                     data=json.dumps({
                                         "secret": self.server_secret,
                                         "text": text,
                                         "chat": "nao"
                                     }))

        response_text = response.json().get("response")
        return response_text

    def onSpeech(self, speechEvent):
        thread = threading.Thread(target=self.question, args=(speechEvent.text, ))
        self.robotics.threads.append(thread)
        thread.start()
```

## Sistema di Eventi

Il sistema utilizza diversi tipi di eventi per la comunicazione tra moduli:

```python
# Classe base per tutti gli eventi
class Event:
    def __init__(self, robotics):
        self.robotics = robotics

# Eventi specifici
class SpeechEvent(Event):
    def __init__(self, robotics, text):
        Event.__init__(self, robotics)
        self.text = text

class AudioEvent(Event):
    def __init__(self, robotics, duration):
        Event.__init__(self, robotics)
        self.duration = duration

class StopEvent(Event):
    def __init__(self, robotics):
        Event.__init__(self, robotics)
```

## Requisiti

- Python 2.7 (compatibile con NAOqi)
- NAOqi SDK
- SpeechRecognition
- Requests
- FFmpeg (per l'elaborazione audio)

## Utilizzo

Per avviare il sistema:

```python
from robotics import Robotics

if __name__ == "__main__":
    try:
        robotics = Robotics()
        robotics.start()
        
        # Mantieni il programma in esecuzione
        while True:
            continue
    except KeyboardInterrupt:
        robotics.stop()
```

## Configurazione

Prima di utilizzare il sistema, è necessario configurare:

1. L'indirizzo IP del robot NAO nel file `proxy.py`:
   ```python
   def __init__(self, robotics, ip = "192.168.1.100", port = 9559):
       self.ip = ip
       self.port = port
   ```

2. Le credenziali del server AI nel file `chatAssistant.py`:
   ```python
   self.server_ip = "your-ai-server-ip"
   self.server_port = "your-ai-server-port"
   self.server_secret = "your-secret-token"
   ```

3. Le credenziali del server TTS nel file `voiceManager.py`:
   ```python
   self.server_ip = "your-tts-server-ip"
   self.server_port = "your-tts-server-port"
   self.server_secret = "your-tts-secret-token"
   ```

## Estensione del Sistema

Per aggiungere nuove funzionalità, segui questi passaggi:

1. Creare una nuova classe di evento che estende `Event`:
   ```python
   class MyCustomEvent(Event):
       def __init__(self, robotics, custom_data):
           Event.__init__(self, robotics)
           self.custom_data = custom_data
   ```

2. Implementare un listener che risponde all'evento:
   ```python
   class MyCustomModule:
       def __init__(self, robotics):
           self.robotics = robotics
           robotics.eventManager.addListener(self)
       
       def onMyCustom(self, myCustomEvent):
           # Gestisci l'evento
           print("Ricevuto evento personalizzato con dati: " + myCustomEvent.custom_data)
           # Esegui azioni in risposta all'evento
   ```

3. Registrare il listener con `eventManager.addListener()`:
   ```python
   # In robotics.py, aggiungi:
   self.myCustomModule = MyCustomModule(self)
   ```

4. Inviare l'evento quando necessario:
   ```python
   self.robotics.eventManager.sendEvent(MyCustomEvent(self.robotics, "dati personalizzati"))
   ```

## Conclusione

Tutte queste innovative funzioni compongono lo scheletro del nostro progetto e delle nostre future iniziative. Il lavoro svolto oggi renderà lo sviluppo su NAO un posto più semplice da esplorare e permetterà a tanti studenti curiosi come noi di ampliare gli orizzonti verso un qualcosa di sempre più elaborato ma di semplice interazione.

Tale framework è adatto ad ogni casistica di utilizzo ed a tal fine ci auguriamo di compiere un enorme contributo verso la comunità di studenti che un giorno vorranno sviluppare soluzioni innovative in modo semplice ed efficace.

Questo potentissimo framework è oggi disponibile in rete ed utilizzabile dalle future menti che dovranno plasmare l'innovazione portata avanti dallo sviluppo su NAO. In quanto pionieri dell'opensource siamo consapevoli che parte dei moduli realizzati non saremmo oggi riusciti a svilupparli senza il contributo del codice libero, e siamo pronti ad accogliere contributi futuri.

## Autori

Questo progetto è stato sviluppato da uno studente dell'Istituto Verona Trento:

- Mirko Cerasi ([@Madacaos](https://github.com/Madacaos))

## Licenza

Questo progetto è distribuito con licenza [Creative Commons Attribution 4.0 International (CC BY 4.0)](http://creativecommons.org/licenses/by/4.0/).

Ciò significa che sei libero di:
- Condividere — copiare e ridistribuire il materiale in qualsiasi mezzo o formato
- Adattare — remixare, trasformare e sviluppare il materiale per qualsiasi scopo, anche commerciale

A queste condizioni:
- **Attribuzione** — Devi riconoscere una menzione di paternità adeguata, fornire un link alla licenza e indicare se sono state effettuate delle modifiche. Puoi fare ciò in qualsiasi maniera ragionevole possibile, ma non con modalità tali da suggerire che il licenziante avalli te o il tuo utilizzo del materiale.

Per maggiori dettagli, consulta il file [LICENSE](LICENSE) incluso in questo repository.