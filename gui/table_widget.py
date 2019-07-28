from PyQt5.QtWidgets import QTableWidget

class TableWidget(QTableWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Table Window")
        self.setColumnCount(2)
        self.setRowCount(10)
        self.setAlternatingRowColors(True)
        self.setHorizontalHeaderLabels(["Time", "Pressure"])
