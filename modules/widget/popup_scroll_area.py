from PyQt5.QtWidgets import QScrollArea

from modules.other.global_variables import GlobalVariables


class PopupScrollArea(QScrollArea):

    def wheelEvent(self, event):
        direction = 1 if event.angleDelta().y() < 0 else -1

        scroll = self.horizontalScrollBar()
        scroll.setValue(scroll.value() + GlobalVariables.EMPTY_SCROLL_VALUE * direction)
