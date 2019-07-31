import sys
from PT_Tester import MainWindow
from PyQt5.QtGui import QIcon
from PyQt5.Qt import QApplication


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
