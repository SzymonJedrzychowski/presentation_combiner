import json
from ctypes import windll
from os import listdir, remove, path, makedirs
from time import time

from PIL import Image, ImageDraw, ImageFont
from PyQt5.QtCore import QTimer, Qt, QSize, QThread
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QMainWindow, QGridLayout, QWidget, QScrollArea, QVBoxLayout, QHBoxLayout, QLabel, \
    QPushButton, QFileDialog, QDialog, QToolTip

from .popup_progress_bar import PopupProgressBar
from .popup_window import PopupWindow
from .settings_window import SettingsWindow
from .slide_image import SlideImage
from .worker import Worker


class MainScreen(QMainWindow):

    def __init__(self):
        super(MainScreen, self).__init__()
        self.setWindowTitle('Kombinator prezentacji')

        self.organize_and_load_structures()

        self.image_list = []
        self.directory_content = []
        self.selected_image = None
        self.max_width = self.screen().availableSize().width() - 450
        self.scroll_direction = 0
        self.drag_start_time = 0
        self.settings = self.load_settings()

        self.scroll_timer = self.create_timer()

        self.setAcceptDrops(True)

        self.create_progress_bar()
        self.setup_layout()
        self.set_icon(self)

    def load_settings(self):
        if path.exists('data/settings.json'):
            with open('data/settings.json') as f:
                return json.load(f)
        else:
            return {
                "dpi": 100
            }

    def setup_layout(self):
        self.main_layout = QGridLayout()
        self.main_widget = QWidget()

        self.slides_area = self.create_slides_area()
        self.view_area = self.create_view_area()

        self.main_layout.addLayout(self.slides_area, 0, 0, 1, 1)
        self.main_layout.addLayout(self.view_area, 0, 1, 1, 1)

        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)

    def create_progress_bar(self):
        self.popup_progress_bar = PopupProgressBar()
        self.set_icon(self.popup_progress_bar)

        self.worker = Worker(self.settings)
        self.thread = QThread()
        self.worker.int_ready.connect(self.popup_progress_bar.on_count_changed)
        self.worker.moveToThread(self.thread)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.popup_progress_bar.hide)
        self.worker.finished.connect(self.on_load_finish)
        self.thread.started.connect(self.worker.proc_counter)

    def create_slides_area(self):
        slides_area = QGridLayout()
        self.scrollable_area = self.create_scrollable_area()
        buttons_area = self.create_buttons_area()

        slides_area.addWidget(self.scrollable_area, 0, 0, 1, 1)
        slides_area.addLayout(buttons_area, 1, 0, 1, 1)

        return slides_area

    def create_scrollable_area(self):
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

    def create_slide(self, image_index):
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

    def update_scroll_value(self):
        scroll_bar = self.scrollable_area.verticalScrollBar()
        scroll_bar_value = scroll_bar.value()
        scroll_max_value = self.scrollable_area.geometry().height()
        if self.scroll_direction == -1:
            scroll_bar.setValue(max(scroll_bar_value - 5, 0))
        elif self.scroll_direction == 1:
            scroll_bar.setValue(min(scroll_bar_value + 5, scroll_max_value))

    def get_breakpoints_without_drop_widget(self, drop_widget):
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

    def update_list(self, event):
        drop_position_y = event.pos().y()
        drop_widget = event.source()

        image_box_breakpoint_list, image_to_add = self.get_breakpoints_without_drop_widget(drop_widget)

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

    def reapply_selection(self, event):
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
        self.update_selected_slide(pixmap)

    def update_selected_slide(self, pixmap):
        if pixmap.width() > self.screen().availableSize().width()-450:
            pixmap = pixmap.scaledToWidth(self.screen().availableSize().width()-450)

        if pixmap.height() > self.screen().availableSize().height():
            pixmap = pixmap.scaledToHeight(self.screen().availableSize().height())

        self.selected_slide.setPixmap(pixmap)

    def create_view_area(self):
        view_area = QGridLayout()

        if self.selected_image is not None:
            image = QPixmap(self.image_list[self.selected_image])
        else:
            image = self.default_image

        pixmap = image.scaledToWidth(self.max_width)

        self.selected_slide = QLabel()
        self.update_selected_slide(pixmap)
        view_area.addWidget(self.selected_slide)
        view_area.setAlignment(self.selected_slide, Qt.AlignHCenter)

        return view_area

    def create_buttons_area(self):
        layout = QHBoxLayout()

        font = self.font()
        font.setPointSize(18)
        QToolTip.setFont(font)

        self.add_button = QPushButton()
        self.remove_button = QPushButton()
        self.save_button = QPushButton()
        self.reset_button = QPushButton()
        self.settings_button = QPushButton()

        # https://www.flaticon.com/free-icons/add - Add icons created by reussy - Flaticon
        self.add_button.setIcon(QIcon('data/add.png'))
        self.add_button.setIconSize(QSize(32, 32))
        self.add_button.setToolTip("Dodaj slajdy")

        self.add_button.clicked.connect(self.load_files)

        # https://www.flaticon.com/free-icons/less - Less icons created by reussy - Flaticon
        self.remove_button.setIcon(QIcon('data/remove.png'))
        self.remove_button.setDisabled(True)
        self.remove_button.setIconSize(QSize(32, 32))
        self.remove_button.setToolTip("Usuń obecny slajd")

        self.remove_button.clicked.connect(self.remove_current_slide)

        # https://www.flaticon.com/free-icons/close - Close icons created by reussy - Flaticon
        self.reset_button.setIcon(QIcon('data/reset.png'))
        self.reset_button.setDisabled(True)
        self.reset_button.setIconSize(QSize(32, 32))
        self.reset_button.setToolTip("Usuń wszystkie slajdy")

        self.reset_button.clicked.connect(self.reset_slides)

        # https://www.flaticon.com/free-icons/down-arrow - Down arrow icons created by reussy - Flaticon
        self.save_button.setIcon(QIcon('data/download.png'))
        self.save_button.setDisabled(True)
        self.save_button.setIconSize(QSize(32, 32))
        self.save_button.setToolTip("Pobierz pdf")

        self.save_button.clicked.connect(self.save_file)

        # https://www.flaticon.com/free-icons/ui - Ui icons created by reussy - Flaticon
        self.settings_button.setIcon(QIcon('data/settings.png'))
        self.settings_button.setIconSize(QSize(32, 32))
        self.settings_button.setToolTip("Ustawienia")

        self.settings_button.clicked.connect(self.open_settings)

        layout.addWidget(self.add_button)
        layout.addWidget(self.remove_button)
        layout.addWidget(self.reset_button)
        layout.addWidget(self.save_button)
        layout.addWidget(self.settings_button)

        return layout

    def load_files(self):
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
            self.set_icon(error_dialog)

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

    def open_settings(self):
        settings_window = SettingsWindow()
        self.set_icon(settings_window)
        settings_window.exec()
        self.settings = self.load_settings()

    def on_load_finish(self):
        self.add_button.setDisabled(False)
        added_images = [new_file for new_file in listdir('temp') if new_file not in self.directory_content]

        popup_window = PopupWindow(self, self.worker.file, added_images)
        self.set_icon(popup_window)
        popup_window.exec()

        self.update_slide_list(popup_window.selected_images)

    def update_slide_list(self, new_images):
        for image in new_images:
            self.image_list.append('temp/{}'.format(image))

            slide = self.create_slide(len(self.image_list) - 1)
            if self.selected_image is None:
                self.selected_image = 0
                slide.itemAt(1).widget().is_selected = True
                slide.itemAt(1).widget().apply_border()

                selected_image = QPixmap(self.image_list[0])
                pixmap = selected_image.scaledToWidth(self.max_width)

                self.update_selected_slide(pixmap)
            self.image_box.addLayout(slide)

        if self.image_list:
            self.reset_button.setDisabled(False)
            self.remove_button.setDisabled(False)
            self.save_button.setDisabled(False)

    def remove_current_slide(self):
        if self.selected_image is not None:
            layout = self.image_box.itemAt(self.selected_image).layout()
            layout.takeAt(0).widget().deleteLater()
            layout.takeAt(0).widget().deleteLater()
            self.image_box.takeAt(self.selected_image)
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
            self.update_selected_slide(pixmap)

            for image_index in range(self.image_box.count()):
                self.image_box.itemAt(image_index).layout().itemAt(0).widget().setText(str(image_index + 1))

        if not self.image_list:
            self.reset_button.setDisabled(True)
            self.remove_button.setDisabled(True)
            self.save_button.setDisabled(True)

        self.update()

    def reset_slides(self):
        self.selected_image = None

        pixmap = self.default_image.scaledToWidth(self.max_width)
        self.update_selected_slide(pixmap)

        for image_index in reversed(range(self.image_box.count())):
            layout = self.image_box.itemAt(image_index).layout()
            layout.takeAt(0).widget().deleteLater()
            layout.takeAt(0).widget().deleteLater()
            self.image_box.takeAt(image_index)
            self.image_list.pop(image_index)

        self.reset_button.setDisabled(True)
        self.remove_button.setDisabled(True)
        self.save_button.setDisabled(True)

    def save_file(self):
        if not self.image_list:
            return

        file_dialog = QFileDialog()
        self.set_icon(file_dialog)
        filename, _ = file_dialog.getSaveFileName(self, 'Zapisz', '', 'PDF (*.pdf)')

        if filename == '':
            return

        if not filename.endswith('.pdf'):
            filename += '.pdf'

        images = [Image.open(image) for image in self.image_list]

        images[0].save(filename, "PDF", resolution=100.0, save_all=True,
                       append_images=images[1:] if len(images) > 1 else [])

    def set_icon(self, window):
        if self.icon is not None:
            window.setWindowIcon(self.icon)

    def create_default_image(self):
        image = Image.new('RGB', (1280, 720), color=(255, 255, 255))

        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype('arial.ttf', 52)
        text = 'Naciśnij "Dodaj slajdy (+)" aby rozpocząć.'

        draw.text((100, 100), text, (0, 0, 0), font=font)

        image.save('data/temporary_image.jpg')

    def create_timer(self):
        timer = QTimer(self)
        timer.timeout.connect(self.update_scroll_value)
        timer.setInterval(1000 // 60)
        return timer

    def organize_and_load_structures(self):
        if path.exists('data/logo.png'):
            # https://www.flaticon.com/free-icons/squirrel - Squirrel icons created by Freepik - Flaticon
            self.icon = QIcon('data/logo.png')
        else:
            self.icon = None

        if not path.exists('data/temporary_image.jpg'):
            self.create_default_image()

        self.default_image = QPixmap('data/temporary_image.jpg')

        if not path.exists('temp'):
            makedirs('temp')
            windll.kernel32.SetFileAttributesW('temp', 0x02)

        directory_content = listdir('temp')
        if directory_content:
            for file in directory_content:
                remove('temp/{}'.format(file))

    def dragEnterEvent(self, event):
        self.drag_start_time = time()
        event.accept()

    def dragMoveEvent(self, event):
        drag_position_y = event.pos().y()
        geometry = self.scrollable_area.geometry()
        if drag_position_y < geometry.getCoords()[1] + 150 and self.scroll_direction == 0:
            self.scroll_direction = -1
            self.scroll_timer.start()
        elif drag_position_y > geometry.getCoords()[3] - 150 and self.scroll_direction == 0:
            self.scroll_direction = 1
            self.scroll_timer.start()
        elif (drag_position_y < geometry.getCoords()[1] + 150
              or drag_position_y > geometry.getCoords()[3] - 150):
            pass
        else:
            self.scroll_direction = 0

    def dropEvent(self, event):
        if time() - self.drag_start_time > 0.1:
            self.update_list(event)
        else:
            self.reapply_selection(event)

        self.scroll_timer.stop()
        self.scroll_direction = 0

        event.accept()

    def closeEvent(self, event):
        for image_file in listdir('temp'):
            remove('temp/{}'.format(image_file))
