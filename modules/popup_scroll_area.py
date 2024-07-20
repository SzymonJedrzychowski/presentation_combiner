from PyQt5.QtWidgets import QScrollArea


class PopupScrollArea(QScrollArea):

    def wheelEvent(self, event):
        direction = 1 if event.angleDelta().y() < 0 else -1

        scroll = self.horizontalScrollBar()
        scroll.setValue(scroll.value() + 60 * direction)
