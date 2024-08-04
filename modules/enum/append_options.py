from enum import Enum


class AppendOptions(Enum):
    AT_END = 0, 'Na koniec'
    BEFORE_CURRENT = 1, 'Przed obecnie wybranym'
    AFTER_CURRENT = 2, 'Po obecnie wybranym'

    @property
    def index(self) -> int:
        return self.value[0]

    @property
    def display_value(self) -> str:
        return self.value[1]

    @classmethod
    def display_values(cls) -> list[str]:
        return [entry.display_value for entry in cls]

    @classmethod
    def with_index(cls, index: int) -> 'AppendOptions':
        return list(AppendOptions)[index]
