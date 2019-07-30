import sys
from PyQt5.QtWidgets import QPushButton, QColorDialog, QApplication
from PyQt5.QtGui import QColor


class ColorPickerSquare(QPushButton):
    def __init__(self, parent=None, color_name="green"):
        super().__init__(parent)
        self.setAutoFillBackground(True)
        self.name = ""
        self.color = None
        if QColor.isValidColor(color_name):
            self.color = QColor(color_name)
            self.name = color_name
        self.clicked.connect(self.pick_color)
        self.setStyleSheet('background-color: {}'.format(self.color.name()))

    def pick_color(self):
        self.color = QColorDialog.getColor(options=QColorDialog.DontUseNativeDialog)
        self.setStyleSheet('background-color: {}'.format(self.color.name()))
        self.name = self.color.name()


# for testing
if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setOrganizationName("KARE Ltd.")
    app.setOrganizationDomain("KAREyiz.biz")
    app.setApplicationName("PT-Tester")

    form = ColorPickerSquare()
    form.show()
    app.exec()
