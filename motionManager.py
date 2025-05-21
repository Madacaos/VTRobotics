from time import sleep
import threading
import inspect
import random

class MotionManager:
    def __init__(self, robotics):
        self.robotics = robotics
        self.queue = []
        thread = threading.Thread(target=self.task)
        robotics.threads.append(thread)
        thread.start()

    def task(self):
        while True:
            if len(self.queue) == 0:
                sleep(0.5)
                continue

            self.next()
            sleep(1)

    def playGesture(self, gesture, priority = 0):
        self.queue.append(Motion("animations/Stand/Gestures/" + gesture, priority, MotionType.GESTURE))

    def playPosture(self, posture, priority = 0):
        self.queue.append(Motion(posture, priority, MotionType.POSTURE))

    def next(self):
        priority = 0
        index = 0

        for i in range(len(self.queue)):
            motion = self.queue[i]
            if motion.priority > priority:
                index = i
                priority = motion.priority

        motion = self.queue[index]
        self.queue.pop(index)
        if motion.motionType == MotionType.POSTURE:
            self.robotics.proxy.posture.goToPosture(motion.animation, 1.0)
        else:
            self.robotics.proxy.animatedSpeech.say("^run(animations/Stand/Gestures/" + motion.animation + ")")


class Motion:
    def __init__(self, animation, priority, motionType):
        self.animation = animation
        self.priority = priority
        self.motionType = motionType

class TalkGesture():
    BODYTALK1 = "BodyTalk_1"
    BODYTALK2 = "BodyTalk_2"
    BODYTALK3 = "BodyTalk_3"
    BODYTALK4 = "BodyTalk_4"
    BODYTALK5 = "BodyTalk_5"
    BODYTALK6 = "BodyTalk_6"
    BODYTALK7 = "BodyTalk_7"
    BODYTALK8 = "BodyTalk_8"
    BODYTALK9 = "BodyTalk_9"
    BODYTALK10 = "BodyTalk_10"
    BODYTALK11 = "BodyTalk_11"
    BODYTALK12 = "BodyTalk_12"
    BODYTALK13 = "BodyTalk_13"
    BODYTALK14 = "BodyTalk_14"
    BODYTALK15 = "BodyTalk_15"
    BODYTALK16 = "BodyTalk_16"
    BODYTALK17 = "BodyTalk_17"
    BODYTALK18 = "BodyTalk_18"
    BODYTALK19 = "BodyTalk_19"
    BODYTALK20 = "BodyTalk_20"
    BODYTALK21 = "BodyTalk_21"
    BODYTALK22 = "BodyTalk_22"
    EXPLAIN1 = "Explain_1"
    EXPLAIN2 = "Explain_2"
    EXPLAIN3 = "Explain_3"
    EXPLAIN4 = "Explain_4"
    EXPLAIN5 = "Explain_5"
    EXPLAIN6 = "Explain_6"
    EXPLAIN7 = "Explain_7"
    EXPLAIN8 = "Explain_8"
    EXPLAIN10 = "Explain_10"
    EXPLAIN11 = "Explain_11"
    YOUKNOWWHAT1 = "YouKnowWhat_1"
    YOUKNOWWHAT5 = "YouKnowWhat_5"

    @staticmethod
    def random():
        members = inspect.getmembers(TalkGesture, lambda x: isinstance(x, basestring))
        return random.choice(members)[1]

class MotionType(type):
    GESTURE = "GESTURE"
    POSTURE = "POSTURE"