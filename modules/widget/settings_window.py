from PyQt5.QtCore import QRegExp
from PyQt5.QtWidgets import QDialog, QLabel, QGridLayout, QComboBox, QWidget

from modules.enum.append_options import AppendOptions
from modules.other.settings import Settings
from modules.util.widget_util import WidgetUtil


class SettingsWindow(QDialog):

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
        self.dpi_input = WidgetUtil.create_qline_edit_settings(self.custom_font, self.__validate_values,
                                                               'Im większa wartość, tym lepsza jakość, ale dłuższy czas wczytywania.',
                                                               QRegExp('[1-9][0-9]{1,2}'), self.settings.dpi)
        self.__create_row('dpi', 'DPI (50-150):', self.dpi_input)

    def __create_scroll_speed_settings(self):
        self.scroll_speed_input = WidgetUtil.create_qline_edit_settings(self.custom_font, self.__validate_values,
                                                                        'Co pół sekundy, prędkość przewijania wzrośnie o 5, aż do maksymalnej wartości. Musi być mniejsza niż "Maksymalna prędkość przewijania".',
                                                                        QRegExp('[1-9][0-9]{1,2}'),
                                                                        self.settings.scroll_speed)
        self.__create_row('scroll_speed', 'Początkowa prędkość przewijania (5-100):', self.scroll_speed_input)

    def __create_max_scroll_speed_settings(self):
        self.max_scroll_speed_input = WidgetUtil.create_qline_edit_settings(self.custom_font, self.__validate_values,
                                                                            'Co pół sekundy, prędkość przewijania wzrośnie o 5, aż do maksymalnej wartości. Musi być większa niż "Początkowa prędkość przewijania".',
                                                                            QRegExp('[1-9][0-9]{1,2}'),
                                                                            self.settings.max_scroll_speed)
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
        self.save_button.setDisabled(not self.settings.validate_values(self.inputs))

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
