from copy import deepcopy

from modules.other.history.history_point import HistoryPoint


class History:
    def __init__(self):
        self.history_table = [HistoryPoint([], None, None)]
        self.history_index = 0

    def log_list_state(self, list_state: list[str], selected_image: int | None):
        history_point = HistoryPoint(deepcopy(list_state), selected_image, None)
        self.__add_history_point(history_point)

    def log_rotate(self, list_state: list[str], selected_image: int | None, rotated_image: str):
        history_point = HistoryPoint(deepcopy(list_state), selected_image, rotated_image)
        self.__add_history_point(history_point)

    def get_history_point(self, undo: bool) -> HistoryPoint:
        if undo:
            self.history_index -= 1
            return self.history_table[self.history_index + 1]
        else:
            self.history_index += 1
            return self.history_table[self.history_index]

    def __add_history_point(self, history_point: HistoryPoint):
        if self.history_index + 1 < len(self.history_table):
            self.history_table = self.history_table[:self.history_index + 1]
        past_point = self.history_table[self.history_index]
        history_point.past_list_state = past_point.list_state
        history_point.past_selected_image = past_point.selected_image
        self.history_table.append(history_point)
        self.history_index += 1

    @property
    def allow_undo(self) -> bool:
        return self.history_index > 0

    @property
    def allow_redo(self) -> bool:
        return len(self.history_table) > self.history_index + 1
