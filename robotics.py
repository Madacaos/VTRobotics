from chatAssistant import ChatAssistant
from eventManager import EventManager
from audioCapture import AudioCaptureModule
from motionManager import MotionManager
from speechEvent import SpeechEvent
from utils import Logger
from proxy import Proxy
from test import Test
from naoqi import ALBroker
import traceback
import sys
import os 
from stopEvent import StopEvent
from utils import Logger, LogType

from voiceManager import VoiceManager


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
                        - Maurizio Palano (https://github.com/MrTheShy)
                        - Fabrizio La Rosa (https://github.com/fabrimat)
                """, stripped=False)

    def start(self):
        self.threads = []

        self.proxy = Proxy(robotics=self)
        self.eventManager = EventManager()

        self.eventManager.addListener(Test())
        self.eventManager.sendEvent(SpeechEvent(self, "prova"))

        self.voiceManager = VoiceManager(self)
        self.motionManager = MotionManager(self)

        try:
            self.pythonBroker = ALBroker("pythonBroker", self.proxy.ip, 0, self.proxy.ip, self.proxy.port)
            self.audioCapture = AudioCaptureModule("AudioCapture", self)
            self.audioCapture.calibrate_activation_threshold()
        except RuntimeError as e:
            print("Error initializing broker! ", e)
            traceback.print_exc()
            exit(1)
        self.chatAssistant = ChatAssistant(self)

    def stop(self):
        Logger.log("Preparazione disattivazione di VTRobotics...", log_type=LogType.ERRORE)
        self.eventManager.syncSendEvent(StopEvent(self))
        Logger.log("VTRobotics disattivato con successo!", log_type=LogType.ERRORE)
        os._exit(0)