import requests
import json
import subprocess
import re
from time import sleep
import threading
import os

from audioEvent import AudioEvent
from utils import Logger, LogType


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

    def task(self):
        while True:
            if len(self.queue) > 0:
                self.next()
                duration = self.getDuration("{}/voice.ogg".format(self.path))
                Logger.log("Parlero' per {} secondi".format(duration), LogType.DEBUG)
                self.robotics.eventManager.sendEvent(AudioEvent(robotics=self.robotics, duration=duration))
                sleep(duration)
            sleep(0.5)

    def next(self):
        self.tts(self.queue[0])

        thread = threading.Thread(target=self.robotics.proxy.audioPlayer.playFile, args=("{}/voice.ogg".format(self.path), ))
        self.robotics.threads.append(thread)
        thread.start()

        self.queue.pop(0)

    def say(self, text):
        self.queue.append(text)

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

    def getDuration(self, file_path):
        command = ['ffmpeg', '-i', file_path]
        result = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output = result.communicate()[0].decode()

        # Cerca la riga che contiene la durata
        duration_match = re.search(r"Duration: (\d+:\d+:\d+\.\d+)", output)

        if duration_match:
            duration_string = duration_match.group(1)
            # Parse la durata in ore, minuti, secondi e millisecondi
            hours, minutes, seconds = map(float, duration_string.split(':'))
            duration_seconds = hours * 3600 + minutes * 60 + seconds
            return duration_seconds
        else:
            return None
    
    def onStop(self, stopEvent):
        try:
            self.robotics.proxy.audioPlayer.stopAll()
        except Exception:
            pass
        Logger.log("Modulo VoiceManager disattivato", log_type=LogType.ERRORE)