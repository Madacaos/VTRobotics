from naoqi import ALModule, ALProxy
import speech_recognition as sr

import threading
import time
from time import sleep
import qi

import robotics
from speechEvent import SpeechEvent
from utils import Logger, LogType


class AudioCaptureModule(object):
    def __init__(self, name, robotics):
        super(AudioCaptureModule, self).__init__()

        connection_url = "tcp://" + robotics.proxy.ip + ":" + str(robotics.proxy.port)
        app = qi.Application(["AudioCaptureModule", "--qi-url=" + connection_url])
        robotics.proxy.session.registerService("AudioCaptureModule", self)
        app.start()

        self.audio_device = robotics.proxy.audioDevice
        self.audio_device.enableEnergyComputation()
        self.is_listening = False
        self.is_speech = False
        self.audio_device.subscribe("AudioCaptureModule")

        self.activation_threshold = 0
        self.robotics = robotics
        self.recognizer = sr.Recognizer()
        self.calibration_time = 1

        self.buffer = []
        self.calibrate_activation_threshold()
        self.start_listening()

        self.robotics.eventManager.addListener(self)

        thread = threading.Thread(target=self.checkTask)
        self.robotics.threads.append(thread)
        thread.start()

    def checkTask(self):
        self.timeout = 0
        while True:
            if not self.is_listening:
                self.timeout = 0
                return

            right = self.audio_device.getRightMicEnergy()
            left = self.audio_device.getLeftMicEnergy()
            power = (right + left) / 2

            if power >= self.activation_threshold or self.timeout > 0:
                if power >= self.activation_threshold:
                    self.start_speech()
                    self.timeout = 1

                Logger.log("Sto ascoltando, timeout = "+str(self.timeout))
                Logger.log("buffer size = "+str(len(self.buffer)))
                if self.timeout <= 0.1:
                    Logger.log("Sto processando il buffer")
                    thread = threading.Thread(target=self.process_audio_buffer, args=(self.buffer,))
                    self.robotics.threads.append(thread)
                    thread.start()
                    self.timeout = 0
                else:
                    self.timeout -= 0.1
            else:
                self.stop_speech()

            sleep(0.1)


    def start_listening(self):
        self.audio_device.setClientPreferences("AudioCaptureModule", 16000, 4, 0)
        self.audio_device.subscribe("AudioCaptureModule")
        self.is_listening = True

    def stop_listening(self):
        self.buffer = []
        self.audio_device.unsubscribe("AudioCaptureModule")
        self.is_listening = False

    def stop_speech(self):
        if self.is_speech:
            self.buffer = []
        self.is_speech = False
        self.timeout = 0

    def start_speech(self):
        self.is_speech = True

    def processRemote(self, nbOfChannels, nbOfSamplesByChannel, timeStamp, inputBuffer):
        if inputBuffer is None or not self.is_listening:
            return

        self.buffer.append(inputBuffer)

        if not self.is_speech:
            while len(self.buffer) > 10:
                self.buffer.pop(0)

    def is_audio_active(self):
        energy = self.audio_device.getRightMicEnergy()
        print(str(energy) + " - " + str(self.activation_threshold))
        return energy > self.activation_threshold

    def calibrate_activation_threshold(self):
        Logger.log("Calibrazione dei microfoni in corso...")

        total_energy = 0
        samples = 0
        start_time = time.time()

        while time.time() - start_time < self.calibration_time:
            energy = self.audio_device.getRightMicEnergy()
            total_energy += energy
            samples += 1

        average_energy = total_energy / samples
        self.activation_threshold = average_energy + (average_energy * 0.6) + 190
        Logger.log("Treshold calibrato a "+str(self.activation_threshold))

    def process_audio_buffer(self, buffer):
        audio_data = b''.join(str(b) for b in buffer)
        try:
            Logger.log("Riconoscimento vocale in corso...", LogType.DEBUG)
            audio_data_instance = sr.AudioData(audio_data, 16000, 2)  # Assuming 16kHz, 2 channels
            try:
                text = self.recognizer.recognize_google(audio_data_instance, language="it-IT")
            except sr.UnknownValueError:
                Logger.log("Il riconoscimento vocale non ha sentito nulla!", LogType.ERRORE)
                return
            except sr.RequestError as e:
                Logger.log("Non ho ricevuto nessun responso dalle Google API", LogType.ERRORE)
                return

            self.robotics.eventManager.sendEvent(SpeechEvent(robotics=self.robotics, text=text))
            # aiResponse = assistant_instance.getMessage(text)
            # print("AI said:", aiResponse)
        except sr.UnknownValueError:
            Logger.log("Il riconoscimento vocale non ha sentito nulla!", LogType.ERRORE)
        except sr.RequestError as e:
            Logger.log("Non riesco a mandare richieste ai servizi di Google", LogType.ERRORE)

    def onAudio(self, audioEvent):
        sleep(0.5)
        self.buffer = []
        self.stop_speech()
        sleep(audioEvent.duration)
        self.buffer = []
        self.stop_speech()