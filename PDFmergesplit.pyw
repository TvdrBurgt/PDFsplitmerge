# -*- coding: utf-8 -*-
"""
Created on Sun Jan 23 09:35:22 2022

@author: tvdrb
"""

import os
import sys
import logging


from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QWidget, QGridLayout, QGroupBox, QLineEdit, QPushButton, QLabel, QCheckBox

from PDFmergesplit_backend import PDFMergeSplit

global path
path = os.path.dirname(os.path.realpath(__file__))
os.chdir(path)

class GUI(QWidget):
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
        
        # Label - files indicator
        self.label_filesindicator = QLabel("File added: ")
        
        # Button - search pdf
        button_findpdf = QPushButton(clicked=self.search_file)
        button_findpdf.setIcon(QtGui.QIcon(path+"/Icons/ICON_BROWSE.png"))
        
        # Button - load pdf
        button_openpdf = QPushButton(clicked=self.open_file)
        button_openpdf.setIcon(QtGui.QIcon(path+"/Icons/ICON_OPEN.svg"))
        
        # Button - close pdf
        button_closepdf = QPushButton(clicked=self.close_file)
        button_closepdf.setIcon(QtGui.QIcon(path+"/Icons/ICON_DELETE.png"))
        
        filesearchLayout.addWidget(self.lineedit_filepath, 0, 0, 1, 1)
        filesearchLayout.addWidget(self.label_filesindicator, 1, 0, 1, 4)
        filesearchLayout.addWidget(button_findpdf, 0, 1, 1, 1)
        filesearchLayout.addWidget(button_openpdf, 0, 2, 1, 1)
        filesearchLayout.addWidget(button_closepdf, 0, 3, 1, 1)
        filesearchContainer.setLayout(filesearchLayout)
        filesearchContainer.setMaximumHeight(100)
        
        
        """
        # --------------------------- File preview ----------------------------
        """
        filepreviewContainer = QGroupBox(title="File preview")
        filepreviewLayout = QGridLayout()
        
        # Label - number of pages
        self.label_pagecount = QLabel("Number of pages: ")
        
        # preview
        button = QPushButton(text="Preview", clicked=self.preview)
        
        filepreviewLayout.addWidget(self.label_pagecount, 0, 0, 1, 1)
        filepreviewLayout.addWidget(button, 1, 0, 1, 1)
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
        button_split = QPushButton(text="Split", clicked=self.split)
        
        fileeditorLayout.addWidget(self.lineedit_selectpages, 0, 0, 1, 1)
        fileeditorLayout.addWidget(self.checkbox_stitch, 0, 1, 1, 1)
        fileeditorLayout.addWidget(button_split, 1, 0, 1, 2)
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
        -------------- Start up backend and connect signals/slots--------------
        =======================================================================
        """
        self.backend = PDFMergeSplit()
        
        """
        =======================================================================
        ----------------------------- End of GUI ------------------------------
        =======================================================================
        """
    
    
    def closeEvent(self, event):
        event.accept()
        QtWidgets.QApplication.quit()
    

    def search_file(self):
        filepath, _ = QtWidgets.QFileDialog.getOpenFileName(
            parent=self,
            caption="Choose File",
            directory="",
            filter="PDF Files (*.pdf)" 
        )
        self.backend.filepath = filepath
        self.lineedit_filepath.setText(filepath)
    
    
    def open_file(self):
        filepath = self.backend.filepath
        pdf = open(filepath, "rb")
        self.backend.file = pdf
        self.label_filesindicator.setText("File added: " + filepath.rsplit('/')[-1])
        self.label_pagecount.setText("Number of pages: " + str(self.backend.file.numPages))
    
    
    def close_file(self):
        del self.backend.filepath
        del self.backend.file
        self.lineedit_filepath.setText("")
        self.label_filesindicator.setText("File added: ")
        self.label_pagecount.setText("Number of pages: ")
        
    
    def preview(self):
        print("Here comes a preview window")
    
    def split(self):
        # parse string to comma-separated string array
        pages_intext = self.lineedit_selectpages.text()
        pages_intextarray = list(pages_intext.split(","))
        
        # fill in the page gaps
        pages = []
        for idx,string in enumerate(pages_intextarray):
            if string == '':
                previous_page = pages[-1]
                next_page = int(pages_intextarray[idx+1])
                for p in range(previous_page+1, next_page):
                    pages.append(p)
            else:
                pages.append(int(string))
        self.lineedit_selectpages.setText(str(pages).strip('[]'))
        
        # request backend to execute the split
        if self.checkbox_stitch.isChecked():
            self.backend.split_and_merge(pages)
        else:
            self.backend.split(pages)




if __name__ == "__main__":
    
    def start_logger():
        logging.basicConfig(
            level=logging.WARNING,
            format="%(asctime)s [%(levelname)s] %(message)s",
            handlers=[
                logging.StreamHandler()
            ]
        )
    
    def run_app():
        app = QtWidgets.QApplication(sys.argv)
        mainwin = GUI()
        mainwin.show()
        app.exec_()
    
    
    start_logger()
    run_app()