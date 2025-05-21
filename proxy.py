from audioCapture import AudioCaptureModule
from utils import Network, Logger, LogType
import qi
from naoqi import ALBroker

import traceback

class Proxy():
    def __init__(self, robotics, ip = Network.get_local_ip(), port = 9559):
        self.ip = ip
        self.port = port
        self.robotics = robotics

        try:
            self.session = qi.Session()
            self.session.connect("tcp://"+ ip + ":" + str(port))

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