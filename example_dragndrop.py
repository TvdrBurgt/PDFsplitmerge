import os
import sys

from PyQt5.QtCore import QMimeData
from PyQt5.QtWidgets import QApplication, QDialog, QStackedWidget
from PyQt5.uic import loadUi


class WelcomeScreen(QDialog):
    def __init__(self):
        super().__init__()
        loadUi("GUI_welcome.ui", self)
        self.drag_drop.dragEnterEvent = self.dragEnterEvent
        self.drag_drop.dragMoveEvent = self.dragMoveEvent
        self.drag_drop.dropEvent = self.dropEvent
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if any([url.toString().endswith('.pdf') for url in urls]):
                event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        files = event.mimeData().urls()

        self.fileloader = FileLoaderScreen()

        self.fileloader.process_new_files(files)
        self.fileloader.show()

        event.acceptProposedAction()



class FileLoaderScreen(QDialog):
    def __init__(self):
        super().__init__()
        loadUi("GUI_fileloader.ui")
    
    def process_new_files(self, files):
        files = [url.toString() for url in files]
        for file in files:
            if file.endswith('.pdf'):
                self.add_pdf(file)
            elif file.endswith('.png'):
                self.add_png
    
    def add_pdf(self, file):
        print(file)

    def add_png(self, file):
        print(file)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = WelcomeScreen()
    gui.show()
    sys.exit(app.exec_())