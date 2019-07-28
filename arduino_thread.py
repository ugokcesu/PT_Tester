from time import sleep
from pyfirmata import Arduino, util

from PyQt5.QtCore import QThread, pyqtSignal


class ArduinoThread(QThread):
    sample_received = pyqtSignal(float, name="pressure")
    def __init__(self):
        super().__init__()

    def __del__(self):
        self.exit()

    def quit(self):
        self.