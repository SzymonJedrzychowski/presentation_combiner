from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QDrag, QPixmap
from PyQt5.QtWidgets import QLabel


class SlideImage(QLabel):

    def __init__(self, parent, image, allow_drag=True):
        super(SlideImage, self).__init__()
        self.parent = parent

        self.allow_drag = allow_drag
        self.image = image

        self.pixmap = QPixmap(self.image)

        if not allow_drag:
            # This all can be a settings
            if 2.5 * self.pixmap.width() > self.screen().availableSize().width():
                self.pixmap = self.pixmap.scaledToWidth(int(self.screen().availableSize().width() / 2.5))

            if self.pixmap.height() > self.screen().availableSize().height() - 180:
                self.pixmap = self.pixmap.scaledToHeight(self.screen().availableSize().height() - 180)

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

    def mousePressEvent(self, event):
        if self.allow_drag:
            drag = QDrag(self)
            mime = QMimeData()
            drag.setMimeData(mime)
            drag.exec_(Qt.DropAction.MoveAction)
        else:
            self.is_selected = not self.is_selected
            self.apply_border()
