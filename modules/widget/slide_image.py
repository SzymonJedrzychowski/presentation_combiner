from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QDrag, QPixmap
from PyQt5.QtWidgets import QLabel, QWidget


class SlideImage(QLabel):

    def __init__(self, parent: QWidget, image: str, allow_drag: bool = True):
        super(SlideImage, self).__init__()
        self.parent = parent

        self.allow_drag = allow_drag
        self.image = image

        self.pixmap = QPixmap(self.image)

        if not allow_drag:
            available_width = self.screen().availableSize().width()
            available_height = self.screen().availableSize().height()
            if 2.5 * self.pixmap.width() > available_width:
                self.pixmap = self.pixmap.scaledToWidth(int(available_width / 2.5))

            if self.pixmap.height() > available_height - 180:
                self.pixmap = self.pixmap.scaledToHeight(available_height - 180)

            self.setFixedWidth(self.pixmap.width())
            self.setFixedHeight(self.pixmap.height())
        else:
            self.pixmap = self.pixmap.scaledToWidth(300)
            self.setFixedWidth(self.pixmap.width())
            self.setFixedHeight(self.pixmap.height())

        self.setPixmap(self.pixmap)
        self.is_selected = False
        self.setStyleSheet("border: 2px solid;"
                           "border-color: black;")

    def apply_border(self):
        colour = 'red' if self.is_selected else 'black'
        self.setStyleSheet("border: 2px solid;"
                           "border-color: {};".format(colour))
        self.update()

    def refresh_image(self):
        self.pixmap = QPixmap(self.image)

        self.pixmap = self.pixmap.scaledToWidth(300)
        self.setFixedWidth(self.pixmap.width())
        self.setFixedHeight(self.pixmap.height())

        self.setPixmap(self.pixmap)

    def mousePressEvent(self, event):
        if self.allow_drag:
            drag = QDrag(self)
            mime = QMimeData()
            drag.setMimeData(mime)
            drag.exec_(Qt.DropAction.MoveAction)
        else:
            self.is_selected = not self.is_selected
            self.apply_border()
