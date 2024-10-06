from ctypes import windll
from os import listdir, remove, path, makedirs
from time import time

from PIL import Image
from PyQt5.QtCore import QTimer, Qt, QThread
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QMainWindow, QGridLayout, QWidget, QScrollArea, QVBoxLayout, QHBoxLayout, QLabel, \
    QPushButton, QFileDialog, QDialog, QToolTip

from modules.util.widget_util import WidgetUtil
from modules.enum.append_options import AppendOptions
from modules.widget.popup_progress_bar import PopupProgressBar
from modules.widget.popup_window import PopupWindow
from modules.other.settings import Settings
from modules.widget.settings_window import SettingsWindow
from modules.widget.slide_image import SlideImage
from modules.other.worker import Worker

_TEMPORARY_IMAGE_PATH = 'data/temporary_image.jpg'
_DEFAULT_SCROLL_SPEED = 5
_MAX_SCROLL_SPEED = 25


class MainScreen(QMainWindow):
    main_layout: QGridLayout
    popup_progress_bar: PopupProgressBar
    worker: Worker
    thread: QThread
    scrollable_area: QScrollArea
    image_box: QVBoxLayout
    add_button: QPushButton
    remove_button: QPushButton
    save_button: QPushButton
    reset_button: QPushButton
    settings_button: QPushButton
    default_image: QPixmap
    main_widget: QWidget
    icon: QIcon | None
    selected_slide: QLabel
    view_area: QGridLayout
    scrollable_area: QGridLayout
    buttons_area: QHBoxLayout
    image_buttons_area: QHBoxLayout

    def __init__(self):
        super(MainScreen, self).__init__()
        self.setWindowTitle('Kombinator prezentacji')

        self.__organize_and_load_structures()

        self.image_list: list[str] = []
        self.directory_content: list[str] = []
        self.selected_image: int | None = None
        self.max_width = self.screen().availableSize().width() - 450
        self.scroll_direction = 0
        self.scroll_speed = _DEFAULT_SCROLL_SPEED
        self.drag_start_time = 0
        self.scroll_start_time = 0
        self.settings = Settings()

        self.scroll_timer = self.__create_timer()

        self.setAcceptDrops(True)

        self.__create_progress_bar()
        self.setup_layout()
        self.__set_icon(self)

    def setup_layout(self):
        self.main_layout = QGridLayout()
        self.main_widget = QWidget()

        self.scrollable_area = self.__create_scrollable_area()
        self.view_area = self.__create_view_area()
        self.buttons_area = self.__create_buttons_area()
        self.image_buttons_area = self.__create_image_buttons_area()

        self.main_layout.addWidget(self.scrollable_area, 0, 0, 1, 1)
        self.main_layout.addLayout(self.view_area, 0, 1, 1, 1)
        self.main_layout.addLayout(self.buttons_area, 1, 0, 1, 1)
        self.main_layout.addLayout(self.image_buttons_area, 1, 1, 1, 1)

        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)

    def resize_app(self):
        self.rotate_button.setFixedSize(self.add_button.size())
        self.main_layout.setColumnMinimumWidth(1, self.view_area.geometry().width())

    def __create_progress_bar(self):
        self.popup_progress_bar = PopupProgressBar()
        self.__set_icon(self.popup_progress_bar)

        self.worker = Worker(self.settings)
        self.thread = QThread()
        self.worker.int_ready.connect(self.popup_progress_bar.on_count_changed)
        self.worker.moveToThread(self.thread)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.popup_progress_bar.hide)
        self.worker.finished.connect(self.__on_load_finish)
        self.thread.started.connect(self.worker.proc_counter)

    def __create_scrollable_area(self) -> QScrollArea:
        scrollable_area = QScrollArea()

        self.image_box = QVBoxLayout()
        widget = QWidget()

        widget.setLayout(self.image_box)

        scrollable_area.setMinimumWidth(400)
        scrollable_area.setMaximumWidth(400)
        scrollable_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        scrollable_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scrollable_area.setWidgetResizable(True)
        scrollable_area.setWidget(widget)

        return scrollable_area

    def __create_slide(self, image_index: int) -> QHBoxLayout:
        slide = QHBoxLayout()

        font = self.font()
        font.setPointSize(14)

        page_label = QLabel()
        page_label.setText(str(image_index + 1))
        page_label.setFont(font)
        slide_image = SlideImage(slide, self.image_list[image_index])
        page_label.setFixedWidth(30)

        slide.addWidget(page_label)
        slide.addWidget(slide_image)

        return slide

    def __update_scroll_value(self):
        if self.scroll_start_time != 0:
            elapsed_seconds = int(time() - self.scroll_start_time)
            self.scroll_speed = min(
                (max(elapsed_seconds * 2, 1)) * _DEFAULT_SCROLL_SPEED, _MAX_SCROLL_SPEED)

        scroll_bar = self.scrollable_area.verticalScrollBar()
        scroll_bar_value = scroll_bar.value()
        scroll_bar.setValue(scroll_bar_value + self.scroll_direction * self.scroll_speed)

    def __get_breakpoints_without_drop_widget(self, drop_widget) -> tuple[list[int], str]:
        breakpoints = []

        drop_box_index = 0
        removed_image = None
        while drop_box_index < self.image_box.count():
            current_box = self.image_box.itemAt(drop_box_index)
            if current_box.layout().itemAt(1).widget() == drop_widget:
                self.image_box.removeItem(current_box)
                removed_image = self.image_list.pop(drop_box_index)
                continue
            current_box_geometry = current_box.geometry()
            current_box_y = current_box_geometry.y()
            breakpoints.append(current_box_y + current_box_geometry.height() // 2)
            drop_box_index += 1

        return breakpoints, removed_image

    def __update_list(self, event):
        drop_position_y = event.pos().y()
        drop_widget = event.source()

        image_box_breakpoint_list, image_to_add = self.__get_breakpoints_without_drop_widget(drop_widget)

        scroll_value = self.scrollable_area.verticalScrollBar().value()
        drop_position_y_adjusted = drop_position_y + scroll_value

        drop_box_index = 0
        drop_box_not_placed = True
        while drop_box_index < self.image_box.count():
            if drop_box_not_placed and drop_position_y_adjusted < image_box_breakpoint_list[drop_box_index]:
                self.image_box.insertLayout(drop_box_index, drop_widget.parent)
                self.image_list.insert(drop_box_index, image_to_add)
                drop_box_not_placed = False
            current_box: QVBoxLayout = self.image_box.itemAt(drop_box_index)
            box_label = current_box.itemAt(0).widget()
            box_label.setText(str(drop_box_index + 1))
            drop_box_index += 1

        if drop_box_not_placed:
            self.image_box.insertLayout(drop_box_index, drop_widget.parent)
            self.image_list.insert(drop_box_index, image_to_add)
            current_box = self.image_box.itemAt(drop_box_index)
            box_label = current_box.itemAt(0).widget()
            box_label.setText(str(drop_box_index + 1))

        for slide_index in range(self.image_box.count()):
            if self.image_box.itemAt(slide_index).layout().itemAt(1).widget().is_selected:
                self.selected_image = slide_index
                break

        self.update()

    def __reapply_selection(self, event):
        newly_selected = event.source()

        if newly_selected.is_selected:
            return

        newly_selected.is_selected = True
        newly_selected.apply_border()

        previous_selected = self.image_box.itemAt(self.selected_image).layout().itemAt(1).widget()
        previous_selected.is_selected = False
        previous_selected.apply_border()

        self.selected_image = self.image_list.index(newly_selected.image)

        pixmap = QPixmap(newly_selected.image).scaledToWidth(self.max_width)
        self.__update_selected_slide(pixmap)

    def __update_selected_slide(self, pixmap):
        if pixmap.width() > self.screen().availableSize().width() - 450:
            pixmap = pixmap.scaledToWidth(self.screen().availableSize().width() - 450)

        if pixmap.height() > self.screen().availableSize().height() - 75:
            pixmap = pixmap.scaledToHeight(self.screen().availableSize().height() - 75)

        self.selected_slide.setPixmap(pixmap)

    def __create_view_area(self) -> QGridLayout:
        view_area = QGridLayout()

        if self.selected_image is not None:
            image = QPixmap(self.image_list[self.selected_image])
        else:
            image = self.default_image

        pixmap = image.scaledToWidth(self.max_width)

        self.selected_slide = QLabel()
        self.__update_selected_slide(pixmap)
        view_area.addWidget(self.selected_slide)
        view_area.setAlignment(self.selected_slide, Qt.AlignHCenter)

        return view_area

    def __create_buttons_area(self) -> QHBoxLayout:
        layout = QHBoxLayout()

        font = self.font()
        font.setPointSize(18)
        QToolTip.setFont(font)

        # https://www.flaticon.com/free-icons/add - Add icons created by reussy - Flaticon
        self.add_button = WidgetUtil.create_icon_button('data/add.png', 32, self.__load_files, 'Dodaj slajdy')

        # https://www.flaticon.com/free-icons/less - Less icons created by reussy - Flaticon
        self.remove_button = WidgetUtil.create_icon_button('data/remove.png', 32, self.__remove_current_slide,
                                                           'Usuń obecny slajd', True)

        # https://www.flaticon.com/free-icons/down-arrow - Down arrow icons created by reussy - Flaticon
        self.save_button = WidgetUtil.create_icon_button('data/download.png', 32, self.__save_file, 'Pobierz pdf', True)

        # https://www.flaticon.com/free-icons/close - Close icons created by reussy - Flaticon
        self.reset_button = WidgetUtil.create_icon_button('data/reset.png', 32, self.__reset_slides,
                                                          'Usuń wszystkie slajdy', True)

        # https://www.flaticon.com/free-icons/ui - Ui icons created by reussy - Flaticon
        self.settings_button = WidgetUtil.create_icon_button('data/settings.png', 32, self.__open_settings,
                                                             'Ustawienia')

        layout.addWidget(self.add_button)
        layout.addWidget(self.remove_button)
        layout.addWidget(self.reset_button)
        layout.addWidget(self.save_button)
        layout.addWidget(self.settings_button)

        return layout

    def __create_image_buttons_area(self) -> QHBoxLayout:
        layout = QHBoxLayout()

        font = self.font()
        font.setPointSize(18)
        QToolTip.setFont(font)

        # https://www.flaticon.com/free-icons/mobile-phone - Mobile phone icons created by Freepik - Flaticon
        self.rotate_button = WidgetUtil.create_icon_button('data/rotate-smartphone.png', 32, self.__rotate_image,
                                                           'Obróc', True)

        layout.addWidget(self.rotate_button)

        return layout

    def __load_files(self):
        file = QFileDialog.getOpenFileName(self, 'Wybierz PDF', filter='PDF (*.pdf)')[0]

        if file == "":
            return

        self.directory_content = listdir('temp')
        try:
            self.popup_progress_bar.bar.setValue(0)
            self.add_button.setDisabled(True)
            self.worker.file = file
            self.popup_progress_bar.show()
            self.thread.start()
        except:
            error_dialog = QDialog()
            error_dialog.setWindowTitle('Wystąpił problem')
            error_dialog.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
            self.__set_icon(error_dialog)

            layout = QHBoxLayout()
            widget = QLabel()
            widget.setText(
                'Wystąpił problem w trakcie używania aplikacji.\n'
                'Aplikacja zostanie wyłączona.\n'
                'Jeżeli ten problem wystąpi ponownie, skontaktuj się z autorem.')

            font = self.font()
            font.setPointSize(14)

            widget.setFont(font)

            error_dialog.setLayout(layout)
            layout.addWidget(widget)

            error_dialog.exec()

            self.close()
            return

    def __open_settings(self):
        settings_window = SettingsWindow(self.settings)
        self.__set_icon(settings_window)
        settings_window.exec()
        self.worker.settings = self.settings

    def __on_load_finish(self):
        self.add_button.setDisabled(False)
        added_images = [new_file for new_file in listdir('temp') if new_file not in self.directory_content]

        popup_window = PopupWindow(self, self.worker.file, added_images)
        self.__set_icon(popup_window)
        popup_window.exec()

        if not popup_window.selected_images:
            return

        self.__update_slide_list(popup_window.selected_images)

    def __update_slide_list(self, new_images: list[str]):
        if self.settings.append == AppendOptions.AT_END:
            insert_place = len(self.image_list)
        elif self.settings.append == AppendOptions.BEFORE_CURRENT:
            insert_place = self.selected_image if self.selected_image is not None else 0
        else:
            insert_place = self.selected_image + 1 if self.selected_image is not None else 0

        new_images_list = ['temp/{}'.format(image) for image in new_images]

        if not self.image_list:
            self.image_list = new_images_list
        elif self.settings.append == AppendOptions.AT_END:
            self.image_list = self.image_list + new_images_list
        else:
            self.image_list = self.image_list[:insert_place] + new_images_list + self.image_list[insert_place:]

        for image_index in range(insert_place, insert_place + len(new_images_list)):
            slide = self.__create_slide(image_index)
            if self.selected_image is None:
                self.selected_image = 0
                slide.itemAt(1).widget().is_selected = True
                slide.itemAt(1).widget().apply_border()

                selected_image = QPixmap(self.image_list[0])
                pixmap = selected_image.scaledToWidth(self.max_width)

                self.__update_selected_slide(pixmap)
            self.image_box.insertLayout(image_index, slide)

        if self.settings.append == AppendOptions.BEFORE_CURRENT and self.selected_image >= insert_place and self.image_list != new_images_list:
            self.selected_image += len(new_images_list)

        to_update = insert_place + len(new_images_list)
        while to_update < len(self.image_list):
            self.image_box.itemAt(to_update).layout().itemAt(0).widget().setText(str(to_update + 1))
            to_update += 1

        if self.image_list:
            self.reset_button.setDisabled(False)
            self.remove_button.setDisabled(False)
            self.save_button.setDisabled(False)
            self.rotate_button.setDisabled(False)

    def __remove_current_slide(self):
        if self.selected_image is not None:
            layout = self.image_box.itemAt(self.selected_image).layout()
            layout.takeAt(0).widget().deleteLater()
            layout.takeAt(0).widget().deleteLater()
            self.image_box.takeAt(self.selected_image)

            if path.exists(self.image_list[self.selected_image]):
                remove(self.image_list[self.selected_image])

            self.image_list.pop(self.selected_image)

            if self.image_box.count() > self.selected_image:
                new_item = self.image_box.itemAt(self.selected_image).layout().itemAt(1).widget()
                new_item.is_selected = True
                new_item.apply_border()
                new_image = new_item.image
            elif self.image_box.count() <= self.selected_image and self.selected_image > 0:
                self.selected_image -= 1
                new_item = self.image_box.itemAt(self.selected_image).layout().itemAt(1).widget()
                new_item.is_selected = True
                new_item.apply_border()
                new_image = QPixmap(new_item.image)
            else:
                self.selected_image = None
                new_image = self.default_image

            pixmap = QPixmap(new_image).scaledToWidth(self.max_width)
            self.__update_selected_slide(pixmap)

            for image_index in range(self.image_box.count()):
                self.image_box.itemAt(image_index).layout().itemAt(0).widget().setText(str(image_index + 1))

        if not self.image_list:
            self.reset_button.setDisabled(True)
            self.remove_button.setDisabled(True)
            self.save_button.setDisabled(True)
            self.rotate_button.setDisabled(True)

        self.update()

    def __reset_slides(self):
        self.selected_image = None

        pixmap = self.default_image.scaledToWidth(self.max_width)
        self.__update_selected_slide(pixmap)

        for image_file in listdir('temp'):
            remove('temp/{}'.format(image_file))

        for image_index in reversed(range(self.image_box.count())):
            layout = self.image_box.itemAt(image_index).layout()
            layout.takeAt(0).widget().deleteLater()
            layout.takeAt(0).widget().deleteLater()
            self.image_box.takeAt(image_index)
            self.image_list.pop(image_index)

        self.reset_button.setDisabled(True)
        self.remove_button.setDisabled(True)
        self.save_button.setDisabled(True)
        self.rotate_button.setDisabled(True)

    def __save_file(self):
        if not self.image_list:
            return

        file_dialog = QFileDialog()
        self.__set_icon(file_dialog)
        filename, _ = file_dialog.getSaveFileName(self, 'Zapisz', '', 'PDF (*.pdf)')

        if filename == '':
            return

        if not filename.endswith('.pdf'):
            filename += '.pdf'

        images = [Image.open(image) for image in self.image_list]

        images[0].save(filename, "PDF", resolution=100.0, save_all=True,
                       append_images=images[1:] if len(images) > 1 else [])

    def __set_icon(self, window):
        if self.icon is not None:
            window.setWindowIcon(self.icon)

    def __create_timer(self):
        timer = QTimer(self)
        timer.timeout.connect(self.__update_scroll_value)
        timer.setInterval(1000 // 60)
        return timer

    def __organize_and_load_structures(self):
        if path.exists('data/logo.png'):
            # https://www.flaticon.com/free-icons/squirrel - Squirrel icons created by Freepik - Flaticon
            self.icon = QIcon('data/logo.png')
        else:
            self.icon = None

        if not path.exists(_TEMPORARY_IMAGE_PATH):
            WidgetUtil.create_default_image(_TEMPORARY_IMAGE_PATH)

        self.default_image = QPixmap(_TEMPORARY_IMAGE_PATH)

        if not path.exists('temp'):
            makedirs('temp')
            windll.kernel32.SetFileAttributesW('temp', 0x02)

        directory_content = listdir('temp')
        if directory_content:
            for file in directory_content:
                remove('temp/{}'.format(file))

    def __rotate_image(self):
        image_name = self.image_list[self.selected_image]
        image = Image.open(image_name)

        new_image = image.rotate(-90, expand=True)
        new_image.save(image_name)

        pixmap = QPixmap(image_name).scaledToWidth(self.max_width)
        self.__update_selected_slide(pixmap)

        slide_image = self.image_box.itemAt(self.selected_image).layout().itemAt(1).widget()
        slide_image.refresh_image()

    def dragEnterEvent(self, event):
        self.drag_start_time = time()
        event.accept()

    def dragMoveEvent(self, event):
        drag_position_y = event.pos().y()
        geometry = self.scrollable_area.geometry()
        if drag_position_y < geometry.getCoords()[1] + 150 and self.scroll_direction == 0:
            if self.scroll_direction != -1:
                self.scroll_start_time = time()
            self.scroll_direction = -1
            self.scroll_timer.start()
        elif drag_position_y > geometry.getCoords()[3] - 150 and self.scroll_direction == 0:
            if self.scroll_direction != 1:
                self.scroll_start_time = time()
            self.scroll_direction = 1
            self.scroll_timer.start()
        elif (drag_position_y < geometry.getCoords()[1] + 150
              or drag_position_y > geometry.getCoords()[3] - 150):
            pass
        else:
            self.scroll_timer.stop()
            self.scroll_direction = 0
            self.scroll_speed = _DEFAULT_SCROLL_SPEED

    def dropEvent(self, event):
        if time() - self.drag_start_time > 0.1:
            self.__update_list(event)
        else:
            self.__reapply_selection(event)

        self.scroll_timer.stop()
        self.scroll_direction = 0

        event.accept()

    def closeEvent(self, event):
        for image_file in listdir('temp'):
            remove('temp/{}'.format(image_file))
