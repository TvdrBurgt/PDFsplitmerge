"""
Features to add:
- Connect model
- Drag/drop files
- Add multiple files
- Merge pages from multiple files
"""


import os
import sys


from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import QObject, QSize
from PyQt5.QtWidgets import QWidget, QApplication, QGridLayout, QGroupBox, QLineEdit, QPushButton, QLabel, QCheckBox, QProgressBar
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings

from PyPDF2 import PdfWriter, PdfReader



class View(QWidget):
    def __init__(self):
        super().__init__()
        """
        =======================================================================
        ----------------------------- Start of GUI ----------------------------
        =======================================================================
        """
        """
        # ---------------------- General widget settings ----------------------
        """
        self.setWindowTitle("PDF split and merge")
        
        """
        # ---------------------------- Select file ----------------------------
        """
        filesearchContainer = QGroupBox(title="Select file")
        filesearchLayout = QGridLayout()

        # LineEdit - file path
        self.lineedit_filepath = QLineEdit()
        self.lineedit_filepath.setPlaceholderText("File path")
        self.lineedit_filepath.setMaximumHeight(20)

        # Label - files indicator
        self.label_filesindicator = QLabel("Files added: ")
        self.label_filesindicator.setMaximumHeight(20)

        # Button - search pdf
        self.button_findpdf = QPushButton()
        self.button_findpdf.setIcon(QtGui.QIcon("./Icons/ICON_OPEN.svg"))
        self.button_findpdf.setToolTip("Select a PDF file")

        # Button - close pdf
        self.button_closepdf = QPushButton()
        self.button_closepdf.setIcon(QtGui.QIcon("./Icons/ICON_DELETE.png"))
        self.button_closepdf.setToolTip("Remove PDF file")

        filesearchLayout.addWidget(self.lineedit_filepath, 0, 0, 1, 1)
        filesearchLayout.addWidget(self.label_filesindicator, 1, 0, 1, 3)
        filesearchLayout.addWidget(self.button_findpdf, 0, 1, 1, 1)
        filesearchLayout.addWidget(self.button_closepdf, 0, 2, 1, 1)
        filesearchContainer.setLayout(filesearchLayout)
        filesearchContainer.setMaximumHeight(100)

        """
        # --------------------------- File preview ----------------------------
        """
        filepreviewContainer = QGroupBox(title="File preview")
        filepreviewLayout = QGridLayout()

        # Label - number of pages
        self.label_pagecount = QLabel("Number of pages: ")
        self.label_pagecount.setMaximumHeight(20)

        # WebView - preview
        self.webview_preview = QWebEngineView()
        self.webview_preview.setMinimumSize(320,490)

        filepreviewLayout.addWidget(self.label_pagecount, 0, 0, 1, 1)
        filepreviewLayout.addWidget(self.webview_preview, 1, 0, 1, 1)
        filepreviewContainer.setLayout(filepreviewLayout)

        """
        # ----------------------------- Edit file -----------------------------
        """
        fileeditorContainer = QGroupBox(title="Edit file")
        fileeditorLayout = QGridLayout()

        # Lineedit - select pages
        self.lineedit_selectpages = QLineEdit()
        self.lineedit_selectpages.setPlaceholderText("Select page numbers comma separated")
        
        # Checkbox - stitch splitted pages
        self.checkbox_stitch = QCheckBox(text="Stitch pages")

        # Button - split pdf
        self.button_split = QPushButton(text="Split")
        
        fileeditorLayout.addWidget(self.lineedit_selectpages, 0, 0, 1, 1)
        fileeditorLayout.addWidget(self.checkbox_stitch, 0, 1, 1, 1)
        fileeditorLayout.addWidget(self.button_split, 1, 0, 1, 2)
        fileeditorContainer.setLayout(fileeditorLayout)
        fileeditorContainer.setMinimumWidth(400)

        """
        ---------------------- Add widgets and set Layout ---------------------
        """
        master = QGridLayout()
        master.addWidget(filesearchContainer, 0, 0, 1, 2)
        master.addWidget(filepreviewContainer, 1, 0, 1, 1)
        master.addWidget(fileeditorContainer, 1, 1, 1, 1)
        self.setLayout(master)

        """
        =======================================================================
        ----------------------------- End of GUI ------------------------------
        =======================================================================
        """

    def file_selector(self) -> str:
        filepath, _ = QtWidgets.QFileDialog.getOpenFileName(
            parent=self,
            caption="Choose File",
            directory="",
            filter="PDF Files (*.pdf)" 
        )
        return filepath

    def show_file(self, filepath, pdf):
        self.lineedit_filepath.setText(filepath)
        self.label_filesindicator.setText("Files added: "+filepath.rsplit('/')[-1])
        self.label_pagecount.setText("Number of pages: "+str(pdf.numPages))

    def hide_file(self):
        self.lineedit_filepath.setText("")
        self.label_filesindicator.setText("File added: ")
        self.label_pagecount.setText("Number of pages: ")

    def show_preview(self, filepath:str) -> None:
        self.webview_preview.settings().setAttribute(QWebEngineSettings.PluginsEnabled, True)
        self.webview_preview.settings().setAttribute(QWebEngineSettings.PdfViewerEnabled, True)
        self.webview_preview.load(QtCore.QUrl.fromUserInput(filepath))
    
    def hide_preview(self):
        self.webview_preview.setHtml('')



class Controller(QObject):
    def __init__(self, view, model):
        super().__init__()
        self._view = view
        self._model = model

        # connect signals and slots
        self._view.button_findpdf.clicked.connect(self.selectpdf)
        self._view.button_closepdf.clicked.connect(self.removepdf)

    def selectpdf(self):
        filepath = self._view.file_selector()
        self._model.pdf = filepath
        self._view.show_file(filepath, self._model.pdf)
        self._view.show_preview(filepath)

    def removepdf(self):
        del self._model.pdf
        self._view.hide_file()
        self._view.hide_preview()


class Model(QObject):
    def __init__(self):
        self._pdf = None
    
    @property
    def pdf(self):
        return self._pdf
    
    @pdf.setter
    def pdf(self, filepath: str):
        self._pdf = PdfReader(filepath, "rb")
    
    @pdf.deleter
    def pdf(self):
        self._pdf = None
    
    def split_and_merge(self, savepath:str, pages:list[int]) -> None:
        output = PdfWriter()
        for i in range(self._pdf.numPages):
            if i+1 in pages:
                output.addPage(self._pdf.getPage(i))
        with open((savepath + "_split&stitched.pdf"), "wb") as outputstream:
            output.write(outputstream)

    def split(self, savepath:str, pages:list[int]) -> None:
        for i in range(self._pdf.numPages):
            if i+1 in pages:
                output = PdfWriter()
                output.addPage(self._pdf.getPage(i))
                with open((savepath + "_page%s.pdf" % (i+1)), "wb") as outputstream:
                    output.write(outputstream)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    model = Model()
    view = View()
    controller = Controller(view, model)
    view.show()
    sys.exit(app.exec_())
