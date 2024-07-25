import pyvips
from PyQt5.QtCore import QObject, pyqtSignal


class Worker(QObject):
    finished = pyqtSignal()
    int_ready = pyqtSignal(int)
    file = None
    image_counter = 0

    def __init__(self, settings):
        super().__init__()
        self.settings = settings

    def proc_counter(self):
        image = pyvips.Image.new_from_file(self.file)
        pdf_length = image.get('n-pages')
        for i in range(image.get('n-pages')):
            image = pyvips.Image.pdfload(self.file, page=i, dpi=self.settings['dpi'])
            image.write_to_file(r'temp\slide_{:05d}.jpg'.format(self.image_counter))
            self.image_counter += 1
            self.int_ready.emit(int(100 * i / pdf_length))

        self.finished.emit()
