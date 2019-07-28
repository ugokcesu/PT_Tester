from time import sleep

from PyQt5.QtCore import QObject, QThread
from PyQt5.QtCore import pyqtSignal
from pyfirmata import Arduino, util
from state import State

class ArduinoWorker(QObject):

    timer_start = pyqtSignal()
    sample_received = pyqtSignal(float)
    stopped = pyqtSignal(State)

    def __init__(self, delay, samples):
        super().__init__()
        self.delay = delay
        self.number_of_samples = samples
        self.CORRECTION = -3.45  # transducer not calibrated?

    # connects to arduino and takes measurements
    # returns complete or aborted to main thread

    def run(self):
        interrupted_flag = False
        try:
            board = Arduino('/dev/cu.usbserial-A600egZF')
        except Exception:
            self.stopped.emit(State.CannotConnect)
            return

        iterator = util.Iterator(board)
        iterator.start()
        pin = board.get_pin('a:5:i')
        sleep(1)

        current_thread = QThread().currentThread()
        self.timer_start.emit()
        counter = 0
        while counter != self.number_of_samples:
            sleep(self.delay)
            pressure = (pin.read() * 5) * 150 / 4 + self.CORRECTION
            print(pressure)
            self.sample_received.emit(pressure)
            if current_thread.isInterruptionRequested():
                interrupted_flag = True
                break
            if not iterator.is_alive():
                self.stopped.emit(State.Disconnected)
                break
            counter += 1

        if interrupted_flag:
            self.stopped.emit(State.Aborted)
        else:
            self.stopped.emit(State.Completed)

        board.exit()


