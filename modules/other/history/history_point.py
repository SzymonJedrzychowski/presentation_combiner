class HistoryPoint:
    past_list_state: list[str]
    past_selected_image: int

    def __init__(self, list_state: list[str] | None, selected_image: int | None, rotated_image: str | None):
        self.list_state = list_state
        self.selected_image = selected_image
        self.rotated_image = rotated_image
