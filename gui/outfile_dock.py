import sys
import os
import time
from math import ceil


from PyQt5.QtWidgets import QMainWindow, QDockWidget, QApplication, QGridLayout, QLabel, QSpinBox,\
    QDoubleSpinBox, QWidget, QCheckBox, QMdiArea, QTableWidget, QTableWidgetItem, QPushButton,\
    QMessageBox, QFrame, QLineEdit, QFileDialog, QSizePolicy
from PyQt5.QtCore import Qt, QThread, QTime, QTimer, QModelIndex
from PyQt5.QtGui import QIcon

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt

from arduino_worker import ArduinoWorker
from state import State, StateMessages, StateStyles
from gui.config_dock import ConfigDock


class OutfileDock(QDockWidget):
    def __init__(self, name, parent):
        super().__init__(name, parent)

        self.setObjectName("OutputDock")
        self.setAllowedAreas(Qt.LeftDockWidgetArea)
        self.setFeatures(QDockWidget.NoDockWidgetFeatures | QDockWidget.DockWidgetClosable)

        self.path_le = QLineEdit(os.path.expanduser("~"))
        self.browse_btn = QPushButton("Select Folder")
        self.name_le = QLineEdit("test.test")
        self.delimiter = ","

        self.layout = QGridLayout()
        self.layout.addWidget(self.path_le, 0, 0)
        self.layout.addWidget(self.browse_btn, 0, 1)
        self.layout.addWidget(self.name_le, 1, 0)
        self.layout.setAlignment(Qt.AlignTop)
