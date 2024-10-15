from json import dump, load
from os.path import exists

from modules.enum.append_options import AppendOptions
from modules.other.global_variables import GlobalVariables

_FILENAME: str = GlobalVariables.SETTINGS


class Settings:
    _dpi: int = 100
    _append: AppendOptions = AppendOptions.AT_END
    _scroll_speed: int = GlobalVariables.DEFAULT_SCROLL_SPEED
    _max_scroll_speed: int = GlobalVariables.DEFAULT_MAX_SCROLL_SPEED
    _dict: dict[str, int] = {
        'dpi': _dpi,
        'append': _append.index,
        'scroll_speed': _scroll_speed,
        'max_scroll_speed': _max_scroll_speed
    }
    _rules: list = []

    def __init__(self):
        self.load()
        self._rules = [
            self.__validate_dpi,
            self.__validate_scroll_speeds
        ]

    @property
    def dpi(self) -> int:
        return self._dpi

    @dpi.setter
    def dpi(self, value: int):
        self._dpi = value
        self._dict['dpi'] = value

    @property
    def append(self) -> AppendOptions:
        return self._append

    @append.setter
    def append(self, value: int):
        self._append = AppendOptions.with_index(value)
        self._dict['append'] = value

    @property
    def scroll_speed(self) -> int:
        return self._scroll_speed

    @scroll_speed.setter
    def scroll_speed(self, value: int):
        self._scroll_speed = value
        self._dict['scroll_speed'] = value

    @property
    def max_scroll_speed(self) -> int:
        return self._max_scroll_speed

    @max_scroll_speed.setter
    def max_scroll_speed(self, value: int):
        self._max_scroll_speed = value
        self._dict['max_scroll_speed'] = value

    def load(self):
        if exists(_FILENAME):
            with open(_FILENAME) as file:
                values = load(file)

            self.dpi = values['dpi']
            self.append = values['append']
            self.scroll_speed = values['scroll_speed']
            self.max_scroll_speed = values['max_scroll_speed']

    def save(self, inputs: dict):
        self.dpi = int(inputs['dpi'].text())
        self.append = int(inputs['append'].currentIndex())
        self.scroll_speed = int(inputs['scroll_speed'].text())
        self.max_scroll_speed = int(inputs['max_scroll_speed'].text())

        with open(_FILENAME, 'w') as file:
            dump(self._dict, file)

    def validate_values(self, inputs: dict) -> bool:
        for rule in self._rules:
            if not rule(inputs):
                return False

        return True

    @staticmethod
    def __validate_dpi(inputs: dict) -> bool:
        dpi_value = inputs['dpi'].text()

        return dpi_value != '' and GlobalVariables.MIN_DPI_VALUE <= int(dpi_value) <= GlobalVariables.MAX_DPI_VALUE

    @staticmethod
    def __validate_scroll_speeds(inputs: dict) -> bool:
        scroll_speed = inputs['scroll_speed'].text()
        max_scroll_speed = inputs['max_scroll_speed'].text()

        scroll_speed_validation = scroll_speed != '' and GlobalVariables.MIN_SCROLL_SPEED <= int(
            scroll_speed) <= GlobalVariables.MAX_SCROLL_SPEED
        max_scroll_speed_validation = max_scroll_speed != '' and GlobalVariables.MIN_SCROLL_SPEED <= int(
            max_scroll_speed) <= GlobalVariables.MAX_SCROLL_SPEED

        return scroll_speed_validation and max_scroll_speed_validation and int(scroll_speed) <= int(max_scroll_speed)
