import json
import os.path

from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, QGridLayout, QToolTip


class SettingsWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Ustawienia')
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.custom_font = self.font()
        self.custom_font.setPointSize(14)

        self.settings = self.load_settings()

        QToolTip.setFont(self.custom_font)

        layout = QGridLayout()

        self.create_dpi_settings(layout)
        self.create_buttons(layout)

        self.setLayout(layout)

    def create_dpi_settings(self, layout):
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

        layout.addWidget(label, 0, 0, 1, 1)
        layout.addWidget(self.dpi_input, 0, 1, 1, 1)

    def create_buttons(self, layout):
        cancel_button = QPushButton(default=False, autoDefault=False)
        cancel_button.setText("Odrzuć")
        cancel_button.setFont(self.custom_font)
        cancel_button.clicked.connect(self.close)

        self.save_button = QPushButton()
        self.save_button.setText("Zapisz")
        self.save_button.setFont(self.custom_font)
        self.save_button.clicked.connect(self.save)
        self.save_button.setAutoDefault(True)

        layout.addWidget(cancel_button, 1, 0, 1, 1)
        layout.addWidget(self.save_button, 1, 1, 1, 1)

    def load_settings(self):
        if os.path.exists('data/settings.json'):
            with open('data/settings.json') as f:
                return json.load(f)
        else:
            return {
                "dpi": 100
            }

    def save(self):
        self.settings['dpi'] = int(self.dpi_input.text())

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
