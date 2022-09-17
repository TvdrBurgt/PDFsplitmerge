import os
import sys

from datetime import datetime
from PyPDF2 import PdfWriter, PdfReader
from PyQt5.QtCore import QObject, QUrl
from PyQt5.QtWidgets import QApplication, QDialog, QFileDialog
from PyQt5.QtWebEngineWidgets import QWebEngineSettings
from PyQt5.uic import loadUi

import resources


"""
To do:
- Give more space to QWebEngine to show page numbers
- Preview button functionality
- unittests
- GUI formatting
- Extend to different datatypes (pip install img2pdf)
- Drag files to GUI (replace File-search bar with a big button)
"""



class View(QDialog):
    def __init__(self):
        super().__init__()
        loadUi("GUI_v1.ui", self)

    def reset_lineedit_filepath(self):
        self.lineedit_filepath.setText("File path")
    
    def reset_lineedit_pages(self):
        self.lineedit_selectpages.setText("Select pages, comma separated")

    def file_load(self) -> str:
        filepath,_ = QFileDialog.getOpenFileName(
            parent=self,
            caption="Choose File",
            directory="",
            filter="PDF Files (*.pdf)" 
        )
        return filepath
    
    def file_save(self) -> str:
        filepath = QFileDialog.getExistingDirectory(
            parent=self,
            caption="Choose save directory"
        )
        return filepath

    def show_added_files(self, filenames:list[str]):
        self.label_files.setText(" | ".join(filenames))

    def show_file_metadata(self, pdf):
        """
        Default dictionary in case entries are not provided by the pdf. We
        also make the metadata keys case insensitive.
        """
        metadata_default = {
            '/author': 'Unknown',
            '/creator': 'Unknown',
            '/producer': 'Unknown',
            '/creationdate': 'XX00010101000000'
        }
        metadata = {k.lower(): v for k,v in pdf.metadata.items()}
        metadata = {**metadata_default, **metadata}

        self.label_pagenumber.setText("%d"%pdf.numPages)
        self.label_author.setText(metadata['/author'])
        self.label_creator.setText(metadata['/creator'])
        self.label_producer.setText(metadata['/producer'])
        self.label_creation_date.setText(
            datetime.strptime(metadata['/creationdate'][2:16], f'%Y%m%d%H%M%S').strftime("%m/%d/%Y, %H:%M:%S")
        )
    
    def remove_file_metadata(self):
        self.label_pagenumber.setText("")
        self.label_author.setText("")
        self.label_creator.setText("")
        self.label_producer.setText("")
        self.label_creation_date.setText("")

    def show_file_preview(self, pdf):
        self.PDFviewer.settings().setAttribute( QWebEngineSettings.PluginsEnabled, True)
        self.PDFviewer.settings().setAttribute( QWebEngineSettings.PdfViewerEnabled, True)
        self.PDFviewer.load(QUrl.fromUserInput(pdf))
    
    def remove_file_preview(self):
        self.PDFviewer.load(QUrl.fromUserInput(""))

    def toggle_split_merge(self):
        self.radiobutton_splitpages.setChecked(not self.radiobutton_splitpages.isChecked)
        self.radiobutton_mergepages.setChecked(not self.radiobutton_mergepages.isChecked)
    
    def get_split_pages(self) -> list[int]:
        pages_intext = self.lineedit_selectpages.text()

        pages = []
        if pages_intext != "":
            pages_intextarray = list(pages_intext.split(","))
            for idx,string in enumerate(pages_intextarray):
                if string == '':
                    previous_page = pages[-1]
                    next_page = int(pages_intextarray[idx+1])
                    for p in range(previous_page+1, next_page):
                        pages.append(p)
                else:
                    pages.append(int(string))
            self.lineedit_selectpages.setText(str(pages).strip('[]'))

        return pages



class Controller(QObject):
    def __init__(self, view, model):
        super().__init__()
        self._view = view
        self._model = model

        # connect file explorer buttons
        self._view.button_findpdf.clicked.connect(self.selectpdf)
        self._view.button_deletepdf.clicked.connect(self.removepdf)

        # connect radiobuttons that split or merge
        self._view.radiobutton_mergepages.toggled.connect(self.toggle_split_mode)

        # connect file preview and execute buttons
        self._view.button_preview.clicked.connect
        self._view.button_confirm.clicked.connect(self.execute)

    def toggle_split_mode(self, mode):
        self._view.toggle_split_merge()
        self._model.toggle_mode()

    def selectpdf(self):
        filepath = self._view.file_load()
        if filepath.endswith('.pdf'):
            self._model.pdf = filepath
            self._view.show_file_metadata(self._model.pdf)
            self._view.show_file_preview(filepath)
            self._view.show_added_files(self._model._pdf_filenames)

    def removepdf(self):
        del self._model.pdf
        if self._model.pdf is not None:
            self._view.show_file_metadata(self._model.pdf)
            self._view.show_file_preview(self._model._pdf_filepaths[-1])
        else:
            self._view.remove_file_preview()
            self._view.remove_file_metadata()
            self._view.reset_lineedit_filepath()
        self._view.show_added_files(self._model._pdf_filenames)
    
    def execute(self):
        pages = self._view.get_split_pages()
        save_folder = self._view.file_save(
            # filename=self._model._pdf_filepaths[-1].split('/')[:-1]
        )
        if save_folder != "":
            self._model.split(pages, save_folder)
            self._view.reset_lineedit_pages()



class Model(QObject):
    def __init__(self):
        self._pdf = None
        self._pdf_filepaths = []
        self._pdf_filenames = []
        self._mode = "split"
    
    @property
    def pdf(self):
        return self._pdf
    
    @pdf.setter
    def pdf(self, filepath: str):
        self._pdf = PdfReader(filepath, "rb")
        self._pdf_filepaths.append(filepath)
        self._pdf_filenames.append(filepath.rsplit('/')[-1])
    
    @pdf.deleter
    def pdf(self):
        if len(self._pdf_filepaths) > 1:
            self._pdf_filepaths.pop()
            self._pdf_filenames.pop()
            self._pdf = PdfReader(self._pdf_filepaths[-1], "rb")
        else:
            self._pdf = None
            self._pdf_filepaths = []
            self._pdf_filenames = []

    def toggle_mode(self):
        if self._mode == "split":
            self._mode = "merge"
        else:
            self._mode = "split"

    def split(self, pages:list[str], folder:str) -> None:
        filename = self._pdf_filenames[-1].rstrip(".pdf")
        if self._mode == "split":
            for i in range(self._pdf.numPages):
                if i+1 in pages:
                    output = PdfWriter()
                    output.addPage(self._pdf.getPage(i))
                    with open(os.path.join(folder, filename+"_page%d.pdf" % (i+1)), "wb") as stream:
                        output.write(stream)
        elif self._mode == "merge":
            for i in range(self._pdf.numPages):
                if i+1 in pages:
                    output.addPage(self._pdf.getPage(i))
            with open(os.path.join(folder, filename, "_splitmerge.pdf"), "wb") as stream:
                output.write(stream)
        else:
            raise Exception("Splitting mode not recognized")
    


class App(QApplication):
    def __init__(self, sys_argv):
        super(App, self).__init__(sys_argv)
        self.model = Model()
        self.view = View()
        self.controller = Controller(self.view, self.model)
        self.view.show()



if __name__ == '__main__':
    app = App(sys.argv)
    sys.exit(app.exec_())
