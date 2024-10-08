from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QGridLayout, QComboBox, QWidget

from modules.enum.append_options import AppendOptions
from modules.other.settings import Settings
from modules.util.widget_util import WidgetUtil


class SettingsWindow(QDialog):
    save_button = None

    def __init__(self, settings: Settings):
        super().__init__()
        WidgetUtil.setup_ui(self, 'Ustawienia', 14)

        self.settings = settings
        self.inputs: dict[str, QWidget] = {}

        self.layout = QGridLayout()

        self.__create_dpi_settings()
        self.__create_scroll_speed_settings()
        self.__create_max_scroll_speed_settings()
        self.__create_append_settings()
        self.__create_buttons()

        self.setLayout(self.layout)

    def __create_dpi_settings(self):
        self.dpi_input = QLineEdit()
        self.dpi_input.setAlignment(Qt.AlignRight)
        self.dpi_input.setFont(self.custom_font)
        self.dpi_input.textEdited.connect(self.__validate_values)
        self.dpi_input.setToolTip('Im większa wartość, tym lepsza jakość, ale dłuższy czas wczytywania.')
        validator = QRegExpValidator(QRegExp('[1-9][0-9]{1,2}'), self.dpi_input)
        self.dpi_input.setPlaceholderText(str(self.settings.dpi))
        self.dpi_input.setText(str(self.settings.dpi))
        self.dpi_input.setValidator(validator)

        self.__create_row('dpi', 'DPI (50-150):', self.dpi_input)

    def __create_scroll_speed_settings(self):
        self.scroll_speed_input = QLineEdit()
        self.scroll_speed_input.setAlignment(Qt.AlignRight)
        self.scroll_speed_input.setFont(self.custom_font)
        self.scroll_speed_input.textEdited.connect(self.__validate_values)
        self.scroll_speed_input.setToolTip(
            'Co pół sekundy, prędkość przewijania wzrośnie o 5, aż do maksymalnej wartości. Musi być mniejsza niż "Maksymalna prędkość przewijania".')
        validator = QRegExpValidator(QRegExp('[1-9][0-9]{1,2}'), self.scroll_speed_input)
        self.scroll_speed_input.setPlaceholderText(str(self.settings.scroll_speed))
        self.scroll_speed_input.setText(str(self.settings.scroll_speed))
        self.scroll_speed_input.setValidator(validator)

        self.__create_row('scroll_speed', 'Początkowa prędkość przewijania (5-100):', self.scroll_speed_input)

    def __create_max_scroll_speed_settings(self):
        self.max_scroll_speed_input = QLineEdit()
        self.max_scroll_speed_input.setAlignment(Qt.AlignRight)
        self.max_scroll_speed_input.setFont(self.custom_font)
        self.max_scroll_speed_input.textEdited.connect(self.__validate_values)
        self.max_scroll_speed_input.setToolTip(
            'Co pół sekundy, prędkość przewijania wzrośnie o 5, aż do maksymalnej wartości. Musi być większa niż "Początkowa prędkość przewijania".')
        validator = QRegExpValidator(QRegExp('[1-9][0-9]{1,2}'), self.max_scroll_speed_input)
        self.max_scroll_speed_input.setPlaceholderText(str(self.settings.max_scroll_speed))
        self.max_scroll_speed_input.setText(str(self.settings.max_scroll_speed))
        self.max_scroll_speed_input.setValidator(validator)

        self.__create_row('max_scroll_speed', 'Maksymalna prędkość przewijania (5-100):', self.max_scroll_speed_input)

    def __create_append_settings(self):
        self.append_input = QComboBox()
        for option in AppendOptions.display_values():
            self.append_input.addItem(option)
        self.append_input.setCurrentIndex(self.settings.append.index)
        self.append_input.setFont(self.custom_font)
        self.append_input.setToolTip('Wybierz gdzie zostaną umieszczone slajdy po ich dodaniu.')

        self.__create_row('append', 'Dodaj slajdy:', self.append_input)

    def __create_buttons(self):
        cancel_button = WidgetUtil.create_button('Odrzuć', self.custom_font, self.close)
        self.save_button = WidgetUtil.create_button('Zapisz', self.custom_font, self.__save)

        index_to_append = len(self.inputs)
        self.layout.addWidget(cancel_button, index_to_append, 0, 1, 1)
        self.layout.addWidget(self.save_button, index_to_append, 1, 1, 1)

    def __save(self):
        self.settings.save(self.inputs)
        self.close()

    def __validate_values(self):
        self.save_button.setDisabled(not self.settings.validate_values(self.inputs))

    def __create_row(self, name: str, label_text: str, input_widget: QWidget):
        label = QLabel()
        label.setText(label_text)
        label.setFont(self.custom_font)

        index_to_append = len(self.inputs)
        self.inputs[name] = input_widget

        self.layout.addWidget(label, index_to_append, 0, 1, 1)
        self.layout.addWidget(input_widget, index_to_append, 1, 1, 1)
