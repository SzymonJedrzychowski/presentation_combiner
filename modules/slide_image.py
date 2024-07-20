from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QDrag, QPixmap
from PyQt5.QtCore import Qt, QMimeData


class SlideImage(QLabel):

    def __init__(self, parent, image, allow_drag=True, default_width=340):
        super(SlideImage, self).__init__()
        self.parent = parent

        self.allow_drag = allow_drag
        self.image = image

        pixmap = QPixmap(self.image).scaledToWidth(default_width)
        self.setPixmap(pixmap)
        self.setFixedWidth(pixmap.width())
        self.setFixedHeight(pixmap.height())
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
