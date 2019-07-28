from PyQt5.QtWidgets import QDockWidget, QGridLayout, QLabel, QSpinBox,\
    QDoubleSpinBox, QCheckBox, QPushButton
from PyQt5.QtCore import Qt


class ConfigDock(QDockWidget):
    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.setObjectName("ConfigurationDock")
        self.setAllowedAreas(Qt.LeftDockWidgetArea)

        self.duration_lb = QLabel("Test Duration")
        self.duration_sb = QSpinBox()
        self.duration_sb.setRange(1, 120)
        self.duration_sb.setValue(5)
        self.duration_unit_lb = QLabel(" Seconds")
        self.sampling_lb = QLabel("Sampling Rate")
        self.sampling_dsb = QDoubleSpinBox()
        self.sampling_dsb.setRange(0.1, 10)
        self.sampling_dsb.setValue(1)
        self.sampling_dsb.setDecimals(2)
        self.sampling_dsb.setSingleStep(0.1)
        self.sampling_unit_lb = QLabel(" Seconds")
        self.show_table_cb = QCheckBox("Show Table")
        self.show_graph_cb = QCheckBox("Show Graph")
        self.start_btn = QPushButton("Start Test")
        self.stop_btn = QPushButton("Stop Test")
        self.stop_btn.setDisabled(True)
        self.start_text_lb = QLabel("Test Start Time")
        self.start_time_lb = QLabel()
        self.end_text_lb = QLabel("Test End Time")
        self.end_time_lb = QLabel()
        self.record_pressure_cb = QCheckBox("Record Pressure")
        self.record_temp_cb = QCheckBox("Record Temperature")
        self.record_pressure_cb.setChecked(True)
        self.record_pressure_cb.setChecked(True)
        self.status_lb = QLabel()

        self.layout = QGridLayout()
        self.layout.addWidget(self.duration_lb, 0, 0)
        self.layout.addWidget(self.duration_sb, 0, 1)
        self.layout.addWidget(self.duration_unit_lb, 0, 2)
        self.layout.addWidget(self.sampling_lb, 1, 0)
        self.layout.addWidget(self.sampling_dsb, 1, 1)
        self.layout.addWidget(self.sampling_unit_lb, 1, 2)
        self.layout.addWidget(self.record_pressure_cb, 2, 0)
        self.layout.addWidget(self.record_temp_cb, 2, 1)
        self.layout.addWidget(self.start_btn, 3, 0)
        self.layout.addWidget(self.stop_btn, 3, 1)
        self.layout.addWidget(self.start_text_lb, 4, 0)
        self.layout.addWidget(self.start_time_lb, 4, 1)
        self.layout.addWidget(self.end_text_lb, 5, 0)
        self.layout.addWidget(self.end_time_lb, 5, 1)
        self.layout.addWidget(self.status_lb, 6, 0, 1, 2)
        self.layout.setAlignment(Qt.AlignTop)

        self.setObjectName("ConfigurationDock")
        self.setAllowedAreas(Qt.LeftDockWidgetArea)
        self.setFeatures(QDockWidget.NoDockWidgetFeatures | QDockWidget.DockWidgetClosable)