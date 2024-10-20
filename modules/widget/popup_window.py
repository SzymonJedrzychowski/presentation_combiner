from os import path, remove
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QLabel, QHBoxLayout, QWidget, QVBoxLayout, QGridLayout

from modules.util.widget_util import WidgetUtil
from modules.widget.popup_scroll_area import PopupScrollArea
from modules.widget.slide_image import SlideImage

_IMAGE_PATH = r'temp/{}'


class PopupWindow(QDialog):

    def __init__(self, parent, file, added_images):
        super().__init__(parent)
        self.parent = parent

        WidgetUtil.setup_ui(self, file, 14)

        self.added_images = added_images
        self.selected_images = []
        self.keep_images = False

        self.__setup_layout()

    def __setup_layout(self):
        font = self.font()
        font.setPointSize(14)

        self.main_layout = QGridLayout()

        self.finish_button = WidgetUtil.create_button('Dodaj wybrane slajdy', font, self.__load_images, True, 'Return')
        self.function_button = WidgetUtil.create_button('Zaznacz wszystkie slajdy', font, self.__process_all_images,
                                                        False, 'Ctrl+A')
        cancel_button = WidgetUtil.create_button('Nie dodawaj slajdów', font, self.close, False, 'Escape')

        self.main_layout.addWidget(self.__create_scrollable_area(), 0, 0, 1, 2)
        self.main_layout.addWidget(self.function_button, 1, 0, 1, 2)
        self.main_layout.addWidget(self.finish_button, 2, 0, 1, 1)
        self.main_layout.addWidget(cancel_button, 2, 1, 1, 1)

        self.setLayout(self.main_layout)

    def __create_scrollable_area(self) -> PopupScrollArea:
        scrollable_area = PopupScrollArea()

        self.image_box = QHBoxLayout()
        widget = QWidget()

        max_height = 0
        max_width = 0
        for image_index in range(len(self.added_images)):
            slide = self.__create_slide(image_index)
            self.image_box.addLayout(slide)
            geometry = slide.itemAt(0).widget().pixmap.size()
            max_height = max(max_height, geometry.height())
            max_width = max(max_width, geometry.width())

        if self.added_images:
            self.setFixedHeight(min(max_height + 180, self.parent.height()))
            self.setFixedWidth(min(int(2.5 * max_width), self.parent.width()))

        widget.setLayout(self.image_box)
        widget.mouseReleaseEvent = self.__update_selected

        scrollable_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scrollable_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        scrollable_area.setWidgetResizable(True)
        scrollable_area.setWidget(widget)

        return scrollable_area

    def __create_slide(self, image_index: int) -> QVBoxLayout:
        slide = QVBoxLayout()

        page_label = QLabel()

        font = self.font()
        font.setPointSize(14)

        page_label.setText(str(image_index + 1))
        page_label.setFont(font)

        slide_image = SlideImage(self, _IMAGE_PATH.format(self.added_images[image_index]), False)
        page_label.setFixedHeight(20)

        slide.addWidget(slide_image)
        slide.addWidget(page_label)

        return slide

    def __update_selected(self, event):
        self.selected_images = []

        for image_index in range(self.image_box.count()):
            image = WidgetUtil.get_image_from_imagebox(self.image_box, image_index)
            if image.is_selected:
                self.selected_images.append(self.added_images[image_index])

        if self.image_box.count() == len(self.selected_images):
            self.function_button.setText('Odznacz wszystkie slajdy')
        else:
            self.function_button.setText('Zaznacz wszystkie slajdy')
        self.function_button.setShortcut('Ctrl+A')

        self.finish_button.setDisabled(len(self.selected_images) == 0)

    def __process_all_images(self):
        new_value = self.image_box.count() == len(self.selected_images)
        for image_index in range(self.image_box.count()):
            widget = WidgetUtil.get_image_from_imagebox(self.image_box, image_index)
            widget.is_selected = not new_value
            widget.apply_border()

        self.__update_selected(None)

    def __load_images(self):
        images_to_remove = [image for image in self.added_images if image not in self.selected_images]
        self.__remove_files(images_to_remove)

        self.keep_images = True
        self.close()

    @staticmethod
    def __remove_files(to_remove: list[str]):
        for image_file in to_remove:
            file_path = _IMAGE_PATH.format(image_file)
            if path.isfile(file_path):
                remove(file_path)

    def closeEvent(self, event):
        if self.keep_images:
            return

        self.selected_images = []
        self.__remove_files(self.added_images)
