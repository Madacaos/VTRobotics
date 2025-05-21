import json
import requests
import threading
import random
from time import sleep
import time

from motionManager import MotionManager, TalkGesture
from utils import Logger, LogType


class ChatAssistant:
    def __init__(self, robotics):
        self.server_ip = "188.14.140.140"
        self.server_port = "5173"
        self.server_url = "http://{}:{}".format(self.server_ip, self.server_port)
        self.server_secret = "yh@itsBbkT&F%&6QBWaMpy^Mv"

        self.server_headers = {
            'Content-Type': 'application/json',
        }

        self.robotics = robotics
        robotics.eventManager.addListener(self)
        self.create_chat("default-comparellobello")

    def create_chat(self, system):
        response = requests.post(self.server_url + "/createChat", headers=self.server_headers,
                                 data=json.dumps({
                                     "secret": self.server_secret,
                                     "system": system,
                                     "chat": "nao",
                                     "model": "llama-3.2-90b-vision-preview"
                                 }))

    def ask(self, text):
        response = requests.post(self.server_url + "/sendMessage", headers=self.server_headers,
                                     data=json.dumps({
                                         "secret": self.server_secret,
                                         "text": text,
                                         "chat": "nao"
                                     }))

        response_text = response.json().get("response")
        return response_text

    def question(self, text):
        self.robotics.voiceManager.say(self.ask(text))

    def onSpeech(self, speechEvent):
        thread = threading.Thread(target=self.question, args=(speechEvent.text, ))
        self.robotics.threads.append(thread)
        thread.start()

    def onAudio(self, audioEvent):
        timeEnd = time.time() * 1000 + (audioEvent.duration * 1000)

        while(time.time() * 1000 < timeEnd):
            self.robotics.motionManager.playGesture(TalkGesture.random())
            sleep(2)