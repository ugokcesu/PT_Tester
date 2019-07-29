import sys
import os
import time
from math import ceil


from PyQt5.QtWidgets import QMainWindow, QApplication, \
    QDoubleSpinBox, QWidget, QCheckBox, QMdiArea, QTableWidget, QTableWidgetItem, QPushButton,\
    QMessageBox, QFrame, QLineEdit, QFileDialog, QSizePolicy
from PyQt5.QtCore import Qt, QThread, QTime, QTimer, QModelIndex
from PyQt5.QtGui import QIcon

import matplotlib.pyplot as plt

from arduino_worker import ArduinoWorker
from state import State, StateMessages, StateStyles
from gui.config_dock import ConfigDock
from gui.outfile_dock import OutfileDock
from gui.table_widget import TableWidget
from gui.plot_windows import PlotWindow
from sample import SampleTypes, SampleNames

__version__ = "1.0.0"


class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)

        # TODO where should I put these?
        self.column_order = [SampleTypes.Time, SampleTypes.Pressure, SampleTypes.Temperature]
        self.recording_types_requested = []
        self.delimiter = ','

        self.ran_once = False
        self.current_row = 0
        self.setWindowTitle("P-T Tester")
        self.arduino_thread = None
        self.arduino_worker = None
        self.test_state = State.ReadyNotRan
        self.output_file = None
        self.ax = None

        # CONFIG DOCK
        self.config_dock = ConfigDock("Test Options", self)
        self.config_dock.start_btn.clicked.connect(self.start_test)
        self.config_dock_widget = QWidget()
        self.config_dock_widget.setLayout(self.config_dock.layout)
        self.config_dock.setWidget(self.config_dock_widget)
        self.config_dock_widget.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.config_dock)
        self.update_status(State.ReadyNotRan)

        # FILE OUTPUT DOCK
        self.outfile_dock = OutfileDock("Output Selection", self)
        self.outfile_dock.browse_btn.clicked.connect(self.select_folder)
        self.outfile_dock_widget = QWidget()
        self.outfile_dock_widget.setLayout(self.outfile_dock.layout)
        self.outfile_dock.setWidget(self.outfile_dock_widget)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.outfile_dock)

        # TABLE Window
        self.table_view_tbl = TableWidget(self)

        # PLOT window
        self.plot_window = PlotWindow(self)

        # MDI SETUP
        self.mdi_area = QMdiArea()
        self.setCentralWidget(self.mdi_area)
        self.mdi_area.addSubWindow(self.table_view_tbl)
        self.mdi_area.addSubWindow(self.plot_window)
        self.mdi_area.tileSubWindows()

    def initialize_plot(self):
        plt.ion()
        self.plot_window.figure.clear()
        self.ax = self.plot_window.figure.add_subplot(111)

    def plot_sample(self, x, y):
        # TODO why doesn't it show the line?
        self.ax.plot(x, y, color='blue', marker='.', linewidth='2', linestyle='-')

    def select_folder(self):
        path = self.outfile_path_le.text()
        if not os.path.isdir(path):
            path = os.path.expanduser("~")

        dir = QFileDialog.getExistingDirectory(self, "Select Working Folder", path)
        if os.path.isdir(dir):
            self.outfile_path_le.setText(dir)

    def start_test(self):
        # is at least 1 type of reading set
        record_p = self.config_dock.record_pressure_cb.isChecked()
        record_t = self.config_dock.record_temp_cb.isChecked()
        if not record_p and not record_t:
            QMessageBox.warning(self, "Invalid Test Parameters", "Must select at least 1 reading type",
                                QMessageBox.Ok)
            return
        # check test parameters
        sample_rate = self.config_dock.sampling_dsb.value()
        nb_samples = ceil(self.config_dock.duration_sb.value() / sample_rate)
        if nb_samples <= 1:
            QMessageBox.warning(self, "Invalid Test Parameters", "Duration too short or sampling rate too large",
                                QMessageBox.Ok)
            return
        if not self.config_dock.record_pressure_cb.isChecked() and not self.config_dock.record_temp_cb.isChecked():
            QMessageBox(self, "Invalid Selection", "At least one type of measurement must be selected",
                        QMessageBox.Ok)
            return
        # check if there is already a test in progress
        if self.test_state==State.InProgress:
            return
        # worker thread will check connection, not done here
        # if test(s) were run before, table may contain data
        if self.test_state != State.ReadyNotRan and self.current_row > 1:
            choice = QMessageBox.question(self, "Starting New Test", "Starting new test will erase current data,\
                                          do you want to continue?",
                                          QMessageBox.Yes | QMessageBox.No)
            if choice == QMessageBox.No:
                return
            else:
                self.table_view_tbl.clearContents()
        # check given folder+file can be created
        if not self.is_out_file_ok():
            return
        # if here, test can begin
        self.recording_types_requested = [SampleTypes.Time]
        if record_p:
            self.recording_types_requested.append(SampleTypes.Pressure)
        if record_t:
            self.recording_types_requested.append(SampleTypes.Temperature)

        self.initialize_table()
        self.initialize_plot()

        # set up arduino worker and signal-slots
        self.arduino_worker = ArduinoWorker(sample_rate, nb_samples, record_p, record_t)
        self.arduino_thread = QThread()
        self.arduino_worker.moveToThread(self.arduino_thread)
        self.arduino_thread.started.connect(self.arduino_worker.run)
        self.arduino_worker.sample_received.connect(self.process_sample)
        self.arduino_worker.timer_start.connect(self.update_test_timers)
        self.config_dock.stop_btn.clicked.connect(self.arduino_thread.requestInterruption)
        self.arduino_worker.stopped.connect(self.stop_test)
        self.arduino_thread.start()

        # gui updates
        # timer is started by worker thread, not here
        # update_gui called by update_status
        self.update_status(State.InProgress)

    def update_gui(self, test_state):
        if test_state == State.ReadyNotRan:
            return
        if test_state == State.InProgress:
            self.config_dock.start_btn.setDisabled(True)
            for child in self.config_dock.widget().children():
                if child.objectName() != self.config_dock.stop_btn.objectName() and isinstance(child, QWidget):
                    child.setDisabled(True)
            self.config_dock.stop_btn.setDisabled(False)
            self.outfile_dock.widget().setDisabled(True)
        else:
            for child in self.config_dock.widget().children():
                if child.objectName() != self.config_dock.stop_btn.objectName() and isinstance(child, QWidget):
                    child.setDisabled(False)
            self.config_dock.stop_btn.setDisabled(True)
            self.outfile_dock.widget().setDisabled(False)

    def is_out_file_ok(self):
        path = self.outfile_dock.path_le.text().strip()
        file = self.outfile_dock.name_le.text().strip()
        full_path = os.path.join(path, file)
        if os.path.isfile(full_path):
            choice = QMessageBox.question(self, "File Exists", "File {} exists, do you want to overwrite?"\
                                          .format(full_path), QMessageBox.Yes | QMessageBox.No)
            if choice == QMessageBox.No:
                self.output_file = None
                return False
        try:
            self.output_file = open(full_path, "w")
        except Exception as e:
            QMessageBox.critical(self, "Output File Error", "Cannot create/overwrite file, error message is:\n"\
                                 + str(e))
            self.output_file = None
            return False
        return True

    def update_test_timers(self):
        cur_time = QTime.currentTime()
        end_time = cur_time.addSecs(self.config_dock.duration_sb.value())
        self.config_dock.start_time_lb.setText(cur_time.toString("hh:mm:ss"))
        self.config_dock.end_time_lb.setText(end_time.toString("hh:mm:ss"))

    def initialize_table(self):
        number_of_columns = len(self.recording_types_requested)
        number_of_samples = ceil(self.config_dock.duration_sb.value() / self.config_dock.sampling_dsb.value())
        self.table_view_tbl.setColumnCount(number_of_columns)
        self.table_view_tbl.setRowCount(number_of_samples)
        headers = []
        for sample_type in self.column_order:
            if sample_type in self.recording_types_requested:
                headers.append(SampleNames.names[sample_type])
        self.table_view_tbl.setHorizontalHeaderLabels(headers)
        self.table_view_tbl.clearContents()
        self.current_row = 0

    def process_sample(self, pressure, temperature):
        current_time = self.current_row * self.config_dock.sampling_dsb.value()
        col = 0
        for recording_type in self.column_order:
            if recording_type in self.recording_types_requested:
                if recording_type == SampleTypes.Time:
                    value = current_time
                elif recording_type == SampleTypes.Pressure:
                    value = pressure
                elif recording_type == SampleTypes.Temperature:
                    value = temperature
                self.table_view_tbl.setItem(self.current_row, col,
                                            QTableWidgetItem("{:.2f}".format(value)))
                col += 1

        self.table_view_tbl.selectRow(self.current_row)
        self.current_row += 1

        self.print_sample(current_time, pressure)
        self.plot_sample(current_time,pressure)

    def print_sample(self, current_time, pressure):
        self.output_file.write(str(current_time) + self.outfile_dock.delimiter + str(pressure) + "\n")

    def stop_test(self, state):
        if self.test_state == State.InProgress:
            self.config_dock.start_btn.setDisabled(False)
            self.config_dock.stop_btn.setDisabled(True)
            self.arduino_thread.quit()
            self.update_status(state)
            self.output_file.close()
            self.arduino_worker = None
            self.arduino_thread = None

    def update_status(self, test_state):
        self.test_state = test_state
        self.config_dock.status_lb.hide()
        QTimer.singleShot(250, self.config_dock.status_lb.show)
        self.config_dock.status_lb.setStyleSheet(StateStyles.styles[test_state])
        self.config_dock.status_lb.setText(StateMessages.messages[test_state])
        self.update_gui(self.test_state)


def main():
    app = QApplication(sys.argv)
    app.setOrganizationName("KARE Ltd.")
    app.setOrganizationDomain("KAREyiz.biz")
    app.setApplicationName("PT-Tester")
    app.setWindowIcon(QIcon("images/icon.png"))
    form = MainWindow()
    form.show()
    app.exec()


if __name__ == "__main__":
    main()
