from math import ceil

from PyQt5.QtWidgets import QDockWidget, QGridLayout, QLabel, QSpinBox,\
    QDoubleSpinBox, QCheckBox, QPushButton, QFrame, QComboBox, QWidget
from PyQt5.QtCore import Qt, QTimer

from gui.color_picker_square import ColorPickerSquare
from state import StateStyles, State, StateMessages


class ConfigDock(QDockWidget):
    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.setObjectName("ConfigurationDock")
        self.setAllowedAreas(Qt.LeftDockWidgetArea)
        self.setFeatures(QDockWidget.NoDockWidgetFeatures)

        self._duration_lb = QLabel("Test Duration")
        self._duration_sb = QSpinBox()
        self._duration_sb.setRange(1, 120)
        self._duration_sb.setValue(5)
        self._duration_unit_lb = QLabel(" Seconds")
        self._sampling_lb = QLabel("Sampling Rate")
        self._sampling_dsb = QDoubleSpinBox()
        self._sampling_dsb.setRange(0.1, 10)
        self._sampling_dsb.setValue(1)
        self._sampling_dsb.setDecimals(2)
        self._sampling_dsb.setSingleStep(0.1)
        self._sampling_unit_lb = QLabel(" Seconds")
        self._show_table_cb = QCheckBox("Show Table")
        self._show_graph_cb = QCheckBox("Show Graph")
        self._start_btn = QPushButton("Start Test")
        self._stop_btn = QPushButton("Stop Test")
        self._stop_btn.setDisabled(True)
        self._stop_btn.setObjectName("stop_btn")
        self._start_text_lb = QLabel("Test Start Time")
        self._start_time_lb = QLabel()
        self._end_text_lb = QLabel("Test End Time")
        self._end_time_lb = QLabel()
        self._record_pressure_cb = QCheckBox("Record Pressure")
        self._pressure_color = ColorPickerSquare(color_name="blue")
        self._pressure_marker = QComboBox()
        self._pressure_marker.addItems([".", "o", "v", "^", "s"])
        self._record_temp_cb = QCheckBox("Record Temperature")
        self._temperature_color = ColorPickerSquare(color_name="green")
        self._temp_marker = QComboBox()
        self._temp_marker.addItems([".", "o", "v", "^", "s"])
        self._record_pressure_cb.setChecked(True)
        self._record_pressure_cb.setChecked(True)
        self._status_lb = QLabel()
        self._status_lb.setFrameShape(QFrame.Box)
        self._status_lb.setFrameStyle(QFrame.Sunken)
        self._status_lb.setAutoFillBackground(True)

        self._grid_layout = QGridLayout()
        self._grid_layout.addWidget(self._duration_lb, 0, 0)
        self._grid_layout.addWidget(self._duration_sb, 0, 1)
        self._grid_layout.addWidget(self._duration_unit_lb, 0, 2)
        self._grid_layout.addWidget(self._sampling_lb, 1, 0)
        self._grid_layout.addWidget(self._sampling_dsb, 1, 1)
        self._grid_layout.addWidget(self._sampling_unit_lb, 1, 2)
        self._grid_layout.addWidget(self._record_pressure_cb, 2, 0)
        self._grid_layout.addWidget(self._pressure_color, 2, 1)
        self._grid_layout.addWidget(self._pressure_marker, 2, 2)
        self._grid_layout.addWidget(self._record_temp_cb, 3, 0)
        self._grid_layout.addWidget(self._temperature_color, 3, 1)
        self._grid_layout.addWidget(self._temp_marker, 3, 2)
        self._grid_layout.addWidget(self._start_btn, 4, 0)
        self._grid_layout.addWidget(self._stop_btn, 4, 1)
        self._grid_layout.addWidget(self._start_text_lb, 5, 0)
        self._grid_layout.addWidget(self._start_time_lb, 5, 1)
        self._grid_layout.addWidget(self._end_text_lb, 6, 0)
        self._grid_layout.addWidget(self._end_time_lb, 6, 1)
        self._grid_layout.addWidget(self._status_lb, 7, 0, 1, 2)
        self._grid_layout.setAlignment(Qt.AlignTop)

        self._widget = QWidget()
        self._widget.setLayout(self._grid_layout)
        self.setWidget(self._widget)

    @property
    def grid_layout(self):
        return self._grid_layout

    @property
    def pressure_color_name(self):
        return self._pressure_color.name

    @property
    def temperature_color_name(self):
        return self._temperature_color.name

    def update_status(self, test_state):
        self._status_lb.hide()
        QTimer.singleShot(250, self._status_lb.show)
        self._status_lb.setStyleSheet(StateStyles.styles[test_state])
        self._status_lb.setText(StateMessages.messages[test_state])
        self.update_gui(test_state)

    def update_gui(self, test_state):
        if test_state == State.ReadyNotRan:
            return
        if test_state == State.InProgress:
            self._start_btn.setDisabled(True)
            for child in self.widget().children():
                if child.objectName() != self._stop_btn.objectName() and isinstance(child, QWidget):
                    child.setDisabled(True)
            self._stop_btn.setDisabled(False)
        else:
            for child in self.widget().children():
                if child.objectName() != self._stop_btn.objectName() and isinstance(child, QWidget):
                    child.setDisabled(False)
            self._stop_btn.setDisabled(True)

    def record_pressure_is_checked(self):
        return self._record_pressure_cb.isChecked()

    def record_temperature_is_checked(self):
        return self._record_temp_cb.isChecked()

    def sample_rate(self):
        return self._sampling_dsb.value()

    def number_of_samples(self):
        return ceil(self._duration_sb.value() / self.sample_rate())

    def duration(self):
        return self._duration_sb.value()

    def set_start_time(self,t):
        self._start_time_lb.setText(t)

    def set_end_time(self, t):
        self._end_time_lb.setText(t)

    def pressure_marker(self):
        return self._pressure_marker.currentText()

    def temp_marker(self):
        return self._temp_marker.currentText()

    def stop_button_slot(self, func):
        self._stop_btn.clicked.connect(func)

    def start_button_slot(self, func):
        self._start_btn.clicked.connect(func)
