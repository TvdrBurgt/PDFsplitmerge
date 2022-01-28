# -*- coding: utf-8 -*-
"""
Created on Sun Jan 23 11:21:46 2022

@author: tvdrb
"""
from PyPDF2 import PdfFileWriter, PdfFileReader
from PyQt5.QtCore import QObject, pyqtSignal

class PDFMergeSplit(QObject):
    """ Documentation
    https://pythonhosted.org/PyPDF2/PdfFileReader.html
    """
    
    progress = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        self._filepath = ""
        self._file = None
        
        
    def open_file(self):
        pdf = PdfFileReader(self.filepath, "rb")
        self.file = pdf

    
    def split_and_merge(self, pages):
        output = PdfFileWriter()
        for i in range(self.file.numPages):
            if i+1 in pages:
                output.addPage(self.file.getPage(i))
        with open((self.filepath.rsplit('/')[-1].rstrip('.pdf') + "_split&stitched.pdf"), "wb") as outputStream:
            output.write(outputStream)
        self.progress.emit(100)
    
    def split(self, pages):
        for i in range(self.file.numPages):
            if i+1 in pages:
                output = PdfFileWriter()
                output.addPage(self.file.getPage(i))
                with open((self.filepath.rsplit('/')[-1].rstrip('.pdf') + "_page%s.pdf" % (i+1)), "wb") as outputStream:
                    output.write(outputStream)
        self.progress.emit(100)


    @property
    def filepath(self):
        return self._filepath
    
    @filepath.setter
    def filepath(self, filepath):
        self._filepath = filepath
    
    @filepath.deleter
    def filepath(self):
        self._filepath = ""
    

    @property
    def file(self):
        return self._file
    
    @file.setter
    def file(self, file):
        pdf = PdfFileReader(file, "rb")
        self._file = pdf
    
    @file.deleter
    def file(self):
        self._file = None

