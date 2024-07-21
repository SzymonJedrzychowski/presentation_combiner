import os.path

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QLabel, QHBoxLayout, QWidget, QVBoxLayout, QPushButton, QGridLayout

from modules.popup_scroll_area import PopupScrollArea
from modules.slide_image import SlideImage


class PopupWindow(QDialog):
    def __init__(self, parent, file, added_images):
        super().__init__(parent)
        self.setWindowTitle(file)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)

        self.added_images = added_images
        self.selected_images = []
        self.keep_images = False

        self.setup_layout()

    def setup_layout(self):
        font = self.font()
        font.setPointSize(14)

        self.main_layout = QGridLayout()

        self.finish_button = QPushButton()
        self.function_button = QPushButton()
        cancel_button = QPushButton()

        self.function_button.setText('Zaznacz wszystkie slajdy')
        self.function_button.setFont(font)
        self.function_button.clicked.connect(self.process_all_images)

        self.finish_button.setText('Dodaj wybrane slajdy')
        self.finish_button.setFont(font)
        self.finish_button.clicked.connect(self.load_images)
        self.finish_button.setDisabled(True)

        cancel_button.setText('Nie dodawaj slajdów')
        cancel_button.setFont(font)
        cancel_button.clicked.connect(self.close)

        self.main_layout.addWidget(self.create_scrollable_area(), 0, 0, 1, 2)
        self.main_layout.addWidget(self.function_button, 1, 0, 1, 2)
        self.main_layout.addWidget(self.finish_button, 2, 0, 1, 1)
        self.main_layout.addWidget(cancel_button, 2, 1, 1, 1)

        self.setLayout(self.main_layout)

    def create_scrollable_area(self):
        scrollable_area = PopupScrollArea()

        self.image_box = QHBoxLayout()
        widget = QWidget()

        for image_index in range(len(self.added_images)):
            slide = self.create_slide(image_index)
            self.image_box.addLayout(slide)

        if self.added_images:
            self.setFixedHeight(slide.itemAt(0).geometry().height() + 180)
            self.setFixedWidth(2 * slide.itemAt(0).geometry().width() + 100)

        widget.setLayout(self.image_box)
        widget.mouseReleaseEvent = self.update_selected

        scrollable_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scrollable_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        scrollable_area.setWidgetResizable(True)
        scrollable_area.setWidget(widget)

        return scrollable_area

    def create_slide(self, image_index):
        slide = QVBoxLayout()

        page_label = QLabel()

        font = self.font()
        font.setPointSize(14)

        page_label.setText(str(image_index + 1))
        page_label.setFont(font)

        slide_image = SlideImage(self, 'temp/{}'.format(self.added_images[image_index]), False, 600)
        page_label.setFixedHeight(20)

        slide.addWidget(slide_image)
        slide.addWidget(page_label)

        return slide

    def update_selected(self, event):
        self.selected_images = []
        for image_index in range(self.image_box.count()):
            image = self.image_box.itemAt(image_index).layout().itemAt(0).widget()
            if image.is_selected:
                self.selected_images.append(self.added_images[image_index])

        if self.image_box.count() == len(self.selected_images):
            self.function_button.setText('Odznacz wszystkie slajdy')
        else:
            self.function_button.setText('Zaznacz wszystkie slajdy')

        self.finish_button.setDisabled(len(self.selected_images) == 0)

    def process_all_images(self):
        new_value = self.image_box.count() == len(self.selected_images)
        for image_index in range(self.image_box.count()):
            widget = self.image_box.itemAt(image_index).layout().itemAt(0).widget()
            widget.is_selected = not new_value
            widget.apply_border()

        self.update_selected(None)

    def load_images(self):
        images_to_remove = [image for image in self.added_images if image not in self.selected_images]
        for image_file in images_to_remove:
            file_path = 'temp/{}'.format(image_file)
            if os.path.isfile(file_path):
                os.remove(file_path)

        self.keep_images = True
        self.close()

    def closeEvent(self, event):
        if self.keep_images:
            return

        self.selected_images = []

        for image_file in self.added_images:
            file_path = 'temp/{}'.format(image_file)
            if os.path.isfile(file_path):
                os.remove(file_path)
