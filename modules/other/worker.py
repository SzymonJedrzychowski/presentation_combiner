from PyQt5.QtCore import QObject, pyqtSignal
from pyvips import Image

from modules.other.settings import Settings

_SAVE_NAME = r'temp\slide_{:05d}.jpg'


class Worker(QObject):
    finished: pyqtSignal = pyqtSignal()
    int_ready: pyqtSignal = pyqtSignal(int)
    file: str = None
    image_counter: int = 0

    def __init__(self, settings: Settings):
        super().__init__()
        self.settings = settings

    def proc_counter(self):
        image = Image.new_from_file(self.file)
        pdf_length = image.get('n-pages')

        for current_page in range(pdf_length):
            image = Image.pdfload(self.file, page=current_page, dpi=self.settings.dpi)
            image.write_to_file(_SAVE_NAME.format(self.image_counter))

            self.image_counter += 1
            self.int_ready.emit(int(100 * current_page / pdf_length))

        self.finished.emit()
