from robotics import Robotics
from time import sleep

if __name__ == "__main__":
    try:
        robotics = Robotics()
        robotics.start()

        while True:
            continue
    except KeyboardInterrupt:
        robotics.stop()