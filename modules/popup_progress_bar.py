from PyQt5.QtWidgets import QWidget, QProgressBar, QVBoxLayout


class PopupProgressBar(QWidget):

    def __init__(self):
        super().__init__()
        self.bar = QProgressBar(self)
        self.bar.setGeometry(30, 40, 500, 75)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.bar)
        self.setLayout(self.layout)
        self.setGeometry(300, 300, 550, 100)
        self.setWindowTitle('Wczytywanie pliku')

    def on_count_changed(self, value):
        self.bar.setValue(value)
