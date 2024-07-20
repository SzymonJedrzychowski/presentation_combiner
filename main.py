from PyQt5.QtWidgets import QApplication
from modules import main_screen
import sys


def main():
    app = QApplication(sys.argv)
    screen = main_screen.MainScreen()
    screen.showMaximized()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
