import os

from PyQt5.QtWidgets import QDockWidget, QGridLayout, QPushButton, QLineEdit, QWidget, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt

from state import State


class OutfileDock(QDockWidget):
    def __init__(self, name, parent):
        super().__init__(name, parent)

        self.setObjectName("OutputDock")
        self.setAllowedAreas(Qt.LeftDockWidgetArea)
        self.setFeatures(QDockWidget.NoDockWidgetFeatures)

        self._path_le = QLineEdit(os.path.expanduser("~"))
        self._browse_btn = QPushButton("Select Folder")
        self._name_le = QLineEdit("test.test")
        self._delimiter = ","

        self._layout = QGridLayout()
        self._layout.addWidget(self._path_le, 0, 0)
        self._layout.addWidget(self._browse_btn, 0, 1)
        self._layout.addWidget(self._name_le, 1, 0)
        self._layout.setAlignment(Qt.AlignTop)

        self._widget = QWidget()
        self._widget.setLayout(self._layout)
        self.setWidget(self._widget)

        self._browse_btn.clicked.connect(self.select_folder)

    def update_gui(self, test_state):
        if test_state == State.InProgress:
            self.widget().setDisabled(True)
        else:
            self.widget().setDisabled(False)

    def is_file_ok(self):
        full_path = self.full_path()
        if os.path.isfile(full_path):
            choice = QMessageBox.question(self, "File Exists", "File {} exists, do you want to overwrite?"
                                          .format(full_path), QMessageBox.Yes | QMessageBox.No)
            if choice == QMessageBox.No:
                return False
        try:
            output_file = open(full_path, "a")
            output_file.close()
        except Exception as e:
            QMessageBox.critical(self, "Output File Error", "Cannot create/overwrite file, error message is:\n"
                                 + str(e))
            return False
        return True

    def select_folder(self):
        path = self._path_le.text()
        if not os.path.isdir(path):
            path = os.path.expanduser("~")

        work_dir = QFileDialog.getExistingDirectory(self, "Select Working Folder", path)
        if os.path.isdir(work_dir):
            self._path_le.setText(work_dir)

    def path(self):
        return self._path_le.text().strip()

    def file(self):
        return self._name_le.text().strip()

    def full_path(self):
        return os.path.join(self.path(), self.file())
