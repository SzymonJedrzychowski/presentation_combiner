import os

vips_bin = os.path.abspath(r'vips-dev-8.15\bin')
os.environ['PATH'] = os.pathsep.join((vips_bin, os.environ['PATH']))

from PyQt5.QtWidgets import QApplication
from modules import main_screen
import sys


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    screen = main_screen.MainScreen()
    screen.showMaximized()
    screen.setFixedSize(screen.screen().availableSize())

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
