from time import sleep

from PyQt5.QtCore import QObject, QThread
from PyQt5.QtCore import pyqtSignal
from pyfirmata import Arduino, util
from state import State
from sample import Sample

from setup_logger import logger


class ArduinoWorker(QObject):

    timer_start = pyqtSignal()
    sample_received = pyqtSignal(Sample)
    stopped = pyqtSignal(State)

    def __init__(self, delay, samples, record_pressure, record_temp):
        super().__init__()
        self.delay = delay
        self.number_of_samples = samples
        self.record_pressure = record_pressure
        self.record_temp = record_temp
        self.CORRECTION = -3.45  # transducer not calibrated?
        self.led_pin = None

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
        pressure_pin = None
        if self.record_pressure:
            pressure_pin = board.get_pin('a:5:i')
        temp_pin = None
        if self.record_temp:
            temp_pin = board.get_pin('a:4:i')
        self.led_pin = board.get_pin('d:2:o')
        sleep(1)
        current_thread = QThread().currentThread()
        self.timer_start.emit()
        # Turn on led to indicate test is running
        self.led_pin.write(1)
        counter = 0
        pressure = Sample.NDV
        temp = Sample.NDV

        while counter != self.number_of_samples:
            sleep(self.delay)
            if self.record_pressure:
                pressure = (pressure_pin.read() * 5) * 150 / 4 + self.CORRECTION
            if self.record_temp:
                temp = (temp_pin.read() * 5) * 212 / 4 + 32 + self.CORRECTION
            logger.info("P and T readings from arduino: {:.2f}, {:.2f}".format(pressure, temp))
            self.sample_received.emit(Sample(pressure, temp))
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

    def blink(self):
        self.led_pin.write(int(not self.led_pin.read()))
        print("hello ledpinread is: {}".format(int(self.led_pin.read())))



