from PIL import Image, ImageDraw, ImageFont
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QToolTip, QPushButton, QDialog, QHBoxLayout, QAction

from modules.other.global_variables import GlobalVariables
from modules.widget.slide_image import SlideImage


class WidgetUtil:
    @staticmethod
    def setup_ui(dialog: QDialog, window_name: str, font_size: int):
        dialog.setWindowTitle(window_name)
        dialog.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        dialog.custom_font = dialog.font()
        dialog.custom_font.setPointSize(font_size)
        QToolTip.setFont(dialog.custom_font)

    @staticmethod
    def create_button(text: str, font: QFont, func, disabled: bool = False) -> QPushButton:
        button = QPushButton()
        button.setText(text)
        button.setFont(font)
        button.clicked.connect(func)
        button.setDisabled(disabled)
        button.setAutoDefault(False)
        button.setDefault(False)
        return button

    @staticmethod
    def create_action(path: str, func, tooltip: str, disabled: bool = False) -> QAction:
        action = QAction()
        action.setIcon(QIcon(path))
        action.setToolTip(tooltip)
        action.triggered.connect(func)
        action.setDisabled(disabled)
        return action

    @staticmethod
    def get_image_from_imagebox(image_box: QHBoxLayout, index: int) -> SlideImage:
        layout = image_box.itemAt(index).layout()
        first_widget = layout.itemAt(0).widget()

        if type(first_widget) is SlideImage:
            return first_widget
        return layout.itemAt(1).widget()

    @staticmethod
    def create_default_image(path: str):
        image = Image.new('RGB', (1280, 720), color=(255, 255, 255))

        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype(GlobalVariables.FONT, 52)
        text = 'Naciśnij "Dodaj slajdy (+)" aby rozpocząć.'

        draw.text((100, 100), text, (0, 0, 0), font=font)

        image.save(path)
