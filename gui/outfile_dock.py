import os

from PyQt5.QtWidgets import QDockWidget, QGridLayout, QPushButton, QLineEdit
from PyQt5.QtCore import Qt


class OutfileDock(QDockWidget):
    def __init__(self, name, parent):
        super().__init__(name, parent)

        self.setObjectName("OutputDock")
        self.setAllowedAreas(Qt.LeftDockWidgetArea)
        self.setFeatures(QDockWidget.NoDockWidgetFeatures)

        self.path_le = QLineEdit(os.path.expanduser("~"))
        self.browse_btn = QPushButton("Select Folder")
        self.name_le = QLineEdit("test.test")
        self.delimiter = ","

        self.layout = QGridLayout()
        self.layout.addWidget(self.path_le, 0, 0)
        self.layout.addWidget(self.browse_btn, 0, 1)
        self.layout.addWidget(self.name_le, 1, 0)
        self.layout.setAlignment(Qt.AlignTop)
