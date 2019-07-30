import sys
import os
from math import ceil

from PyQt5.QtWidgets import QMainWindow, QApplication, \
     QWidget, QMdiArea, QTableWidgetItem,\
    QMessageBox, QFileDialog, QSizePolicy
from PyQt5.QtCore import Qt, QThread, QTime, QTimer
from PyQt5.QtGui import QIcon

import matplotlib.pyplot as plt

from arduino_worker import ArduinoWorker
from state import State, StateMessages, StateStyles
from gui.config_dock import ConfigDock
from gui.outfile_dock import OutfileDock
from gui.table_widget import TableWidget
from gui.plot_windows import PlotWindow
from sample import SampleTypes, SampleNames, Sample

__version__ = "1.0.0"


class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)

        # TODO where should I put these?
        self.column_order = [SampleTypes.Time, SampleTypes.Pressure, SampleTypes.Temperature]
        self.sample_types_requested_ordered = []
        self.delimiter = ','


        self.ran_once = False
        self.current_row = 0
        self.setWindowTitle("P-T Tester")
        self.arduino_thread = None
        self.arduino_worker = None
        self.test_state = State.ReadyNotRan
        self.output_file = None
        self.ax = None
        self.ax_secondaries = dict()
        self.plot_colors = dict()

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
        self.plot_colors[SampleTypes.Pressure] = self.config_dock.pressure_color.name
        self.plot_colors[SampleTypes.Temperature] = self.config_dock.temperature_color.name
        self.plot_window.figure.clear()
        self.ax = self.plot_window.figure.add_subplot(111)
        self.ax.set_ylabel(SampleNames.names[self.sample_types_requested_ordered[0]],
                           color=self.plot_colors[self.sample_types_requested_ordered[0]])
        if len(self.sample_types_requested_ordered) > 1:
            for sample_type in self.sample_types_requested_ordered[1:]:
                self.ax_secondaries[sample_type] = self.ax.twinx()
                self.ax_secondaries[sample_type].set_ylabel(SampleNames.names[sample_type],
                                                            color=self.plot_colors[sample_type])

    def plot_sample(self, current_time, sample):
        # TODO why doesn't it show the line?, only markers are shown.
        marker = dict()
        marker[SampleTypes.Pressure] = self.config_dock.pressure_marker.currentText()
        marker[SampleTypes.Temperature] = self.config_dock.temp_marker.currentText()
        self.ax.plot(current_time, sample.values[self.sample_types_requested_ordered[0]],
                     color=self.plot_colors[self.sample_types_requested_ordered[0]],
                     marker=marker[self.sample_types_requested_ordered[0]], linewidth='2', linestyle='-')

        for sample_type in self.sample_types_requested_ordered[1:]:
            self.ax_secondaries[sample_type].plot(current_time, sample.values[sample_type],\
                                                  color=self.plot_colors[sample_type], marker=marker[sample_type])

    def select_folder(self):
        path = self.outfile_dock.path_le.text()
        if not os.path.isdir(path):
            path = os.path.expanduser("~")

        dir = QFileDialog.getExistingDirectory(self, "Select Working Folder", path)
        if os.path.isdir(dir):
            self.outfile_dock.path_le.setText(dir)

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
        if self.test_state == State.InProgress:
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
        self.sample_types_requested_ordered = []
        for samp_type in self.column_order:
            if samp_type == SampleTypes.Pressure and record_p:
                self.sample_types_requested_ordered.append(SampleTypes.Pressure)
            if samp_type == SampleTypes.Temperature and record_t:
                self.sample_types_requested_ordered.append(SampleTypes.Temperature)

        self.initialize_table()
        self.initialize_file()
        self.initialize_plot()

        # set up arduino worker and signal-slots
        self.initialize_worker(nb_samples, record_p, record_t, sample_rate)
        # reading of measurements starts here
        self.arduino_thread.start()

        # gui updates
        # timer is started by worker thread, not here
        # update_gui called by update_status
        self.update_status(State.InProgress)

    def initialize_worker(self, nb_samples, record_p, record_t, sample_rate):
        self.arduino_worker = ArduinoWorker(sample_rate, nb_samples, record_p, record_t)
        self.arduino_thread = QThread()
        self.arduino_worker.moveToThread(self.arduino_thread)
        self.arduino_thread.started.connect(self.arduino_worker.run)
        self.arduino_worker.sample_received.connect(self.process_sample)
        self.arduino_worker.timer_start.connect(self.update_test_timers)
        self.config_dock.stop_btn.clicked.connect(self.arduino_thread.requestInterruption)
        self.arduino_worker.stopped.connect(self.stop_test)

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
            choice = QMessageBox.question(self, "File Exists", "File {} exists, do you want to overwrite?"
                                          .format(full_path), QMessageBox.Yes | QMessageBox.No)
            if choice == QMessageBox.No:
                self.output_file = None
                return False
        try:
            self.output_file = open(full_path, "w")
        except Exception as e:
            QMessageBox.critical(self, "Output File Error", "Cannot create/overwrite file, error message is:\n"
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
        number_of_columns = len(self.sample_types_requested_ordered) + 1 # +1 for time
        number_of_samples = ceil(self.config_dock.duration_sb.value() / self.config_dock.sampling_dsb.value())
        self.table_view_tbl.setColumnCount(number_of_columns)
        self.table_view_tbl.setRowCount(number_of_samples)
        headers = []
        headers.append(SampleNames.names[SampleTypes.Time])
        for sample_type in self.sample_types_requested_ordered:
            headers.append(SampleNames.names[sample_type])
        self.table_view_tbl.setHorizontalHeaderLabels(headers)
        self.table_view_tbl.clearContents()
        self.current_row = 0

    def initialize_file(self):

        headers = []
        headers.append(SampleNames.names[SampleTypes.Time])
        for sample_type in self.sample_types_requested_ordered:
            headers.append(SampleNames.names[sample_type])
        for index, header in enumerate(headers):
            self.output_file.write(header)
            if index != len(headers)-1:
                self.output_file.write(self.delimiter)
        self.output_file.write("\n")

    def process_sample(self, sample):
        current_time = self.current_row * self.config_dock.sampling_dsb.value()

        self.print_sample_qtable(current_time, sample)
        self.print_sample_csv(current_time, sample)
        self.plot_sample(current_time, sample)

        self.table_view_tbl.selectRow(self.current_row)
        self.current_row += 1

    def print_sample_qtable(self, current_time, sample):
        self.table_view_tbl.setItem(self.current_row, 0,
                                    QTableWidgetItem("{:.2f}".format(current_time)))
        for i, sample_type in enumerate(self.sample_types_requested_ordered, start=1):
            self.table_view_tbl.setItem(self.current_row, i,
                                        QTableWidgetItem("{:.2f}".format(sample.values[sample_type])))

    def print_sample_csv(self, current_time, sample):
        self.output_file.write("{:.2f}".format(current_time) + self.delimiter)
        for index, sample_type in enumerate(self.sample_types_requested_ordered):
            self.output_file.write("{:.2f}".format(sample.values[sample_type]))
            if index != len(self.sample_types_requested_ordered)-1:
                self.output_file.write(self.delimiter)
        self.output_file.write("\n")

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
