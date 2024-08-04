from json import dump, load
from os.path import exists

from modules.enum.append_options import AppendOptions

_FILENAME: str = 'data/settings.json'


class Settings:
    _dpi: int = 100
    _append: AppendOptions = AppendOptions.AT_END
    _dict: dict[str, int] = {
        'dpi': _dpi,
        'append': _append.index
    }
    _rules: list = []

    def __init__(self):
        self.load()
        self._rules = [
            self.__validate_dpi
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

    def load(self):
        if exists(_FILENAME):
            with open(_FILENAME) as file:
                values = load(file)

            self.dpi = values['dpi']
            self.append = values['append']

    def save(self, inputs: dict):
        self.dpi = int(inputs['dpi'].text())
        self.append = int(inputs['append'].currentIndex())

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

        return dpi_value != '' and 50 <= int(dpi_value) <= 150
