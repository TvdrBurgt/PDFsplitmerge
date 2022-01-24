# -*- coding: utf-8 -*-
"""
Created on Sun Jan 23 16:13:28 2022

@author: tvdrb
"""

import os
import unittest

os.chdir("..")
from PDFmergesplit import GUI

class GUITestCase(unittest.TestCase):

    def setUp(self):
        """ 
        The setup method only goes through set up files.
        """
        self.ui = GUI()
    
    def tearDown(self):
        """
        This function will be executed after the unittests.
        """
        pass
            
#%% testcases

    def test_pagegap_fill(self):
        self.ui.lineedit_selectpages.setText('1,2,,6,9,10,,11')
        try:
            self.ui.split()
        except AttributeError as e:
            if "'NoneType' object has no attribute 'numPages'" in str(e):
                print('right error occured')
            else:
                raise
        output_pages_intext = self.ui.lineedit_selectpages.text()
        self.assertEqual(output_pages_intext, '1, 2, 3, 4, 5, 6, 9, 10, 11', 'pages were skipped or added')
        


#%% end of testcases



def suite():
    suite = unittest.TestSuite()
    suite.addTest(GUITestCase('test_pagegap_fill'))
    return suite



if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())