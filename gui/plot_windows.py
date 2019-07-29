
from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt


class PlotWindow(QWidget):
        def __init__(self, parent):
                super().__init__(parent)
                self.setWindowTitle("Plotting Window")
                self.figure = plt.figure()
                self.canvas = FigureCanvas(self.figure)
                self.toolbar = NavigationToolbar(self.canvas, self)
                self.btn = QPushButton("Update Plot")

                self.layout = QGridLayout()
                self.layout.addWidget(self.toolbar, 0, 0)
                self.layout.addWidget(self.canvas, 1, 0)
                self.layout.addWidget(self.btn, 2, 0)
                self.setLayout(self.layout)
