import json
import os.path

from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, QGridLayout, QToolTip, QComboBox


class SettingsWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Ustawienia')
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.custom_font = self.font()
        self.custom_font.setPointSize(14)
        self.append_options = ['Na koniec', 'Przed obecnie wybranym', 'Po obecnie wybranym']

        self.settings = self.load_settings()

        QToolTip.setFont(self.custom_font)

        self.layout = QGridLayout()

        self.create_dpi_settings()
        self.create_append_settings()
        self.create_buttons()

        self.setLayout(self.layout)

    def create_dpi_settings(self):
        label = QLabel()
        label.setText("DPI (50-150):")
        label.setFont(self.custom_font)

        self.dpi_input = QLineEdit()
        self.dpi_input.setAlignment(Qt.AlignRight)
        self.dpi_input.setFont(self.custom_font)
        self.dpi_input.textEdited.connect(self.validate_values)
        self.dpi_input.setToolTip('Im większa wartość, tym lepsza jakość, ale dłuższy czas wczytywania.')
        validator = QRegExpValidator(QRegExp('[1-9][0-9]{1,2}'), self.dpi_input)
        self.dpi_input.setPlaceholderText(str(self.settings['dpi']))
        self.dpi_input.setText(str(self.settings['dpi']))
        self.dpi_input.setValidator(validator)

        self.layout.addWidget(label, 0, 0, 1, 1)
        self.layout.addWidget(self.dpi_input, 0, 1, 1, 1)

    def create_append_settings(self):
        label = QLabel()
        label.setText("Dodaj slajdy:")
        label.setFont(self.custom_font)

        self.append_input = QComboBox()
        for option in self.append_options:
            self.append_input.addItem(option)
        self.append_input.setCurrentIndex(self.settings["append"])
        self.append_input.setFont(self.custom_font)
        self.append_input.setToolTip('Wybierz gdzie zostaną umieszczone slajdy po ich dodaniu.')

        self.layout.addWidget(label, 1, 0, 1, 1)
        self.layout.addWidget(self.append_input, 1, 1, 1, 1)

    def create_buttons(self):
        cancel_button = QPushButton(default=False, autoDefault=False)
        cancel_button.setText("Odrzuć")
        cancel_button.setFont(self.custom_font)
        cancel_button.clicked.connect(self.close)

        self.save_button = QPushButton()
        self.save_button.setText("Zapisz")
        self.save_button.setFont(self.custom_font)
        self.save_button.clicked.connect(self.save)
        self.save_button.setAutoDefault(True)

        self.layout.addWidget(cancel_button, 2, 0, 1, 1)
        self.layout.addWidget(self.save_button, 2, 1, 1, 1)

    def load_settings(self):
        if os.path.exists('data/settings.json'):
            with open('data/settings.json') as f:
                return json.load(f)
        else:
            return {
                "dpi": 100,
                "append": 0
            }

    def save(self):
        self.settings['dpi'] = int(self.dpi_input.text())
        self.settings['append'] = self.append_input.currentIndex()

        with open('data/settings.json', 'w') as f:
            json.dump(self.settings, f)

        self.close()

    def validate_values(self):
        rules = [self.validate_dpi]

        for rule in rules:
            if not rule():
                self.save_button.setDisabled(True)
                return

        self.save_button.setDisabled(False)

    def validate_dpi(self):
        dpi_value = self.dpi_input.text()

        return dpi_value != '' and int(dpi_value) >= 50 and int(dpi_value) <= 150
