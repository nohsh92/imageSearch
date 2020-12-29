import GUI
from PyQt5.QtWidgets import QApplication
import sys


def main():
    app = QApplication(sys.argv)
    ex = GUI.MainGUI()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()