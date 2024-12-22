# -*- coding: utf-8 -*-
"""
Created on Tue Jun 18 10:13:21 2024

@author: klaus
"""

from SAS_PCS_FITTER_KGOETZ91.gui.popups import ErrorMessage
from SAS_PCS_FITTER_KGOETZ91.gui.generalwidget import GeneralWidget

class GeneralGUI(GeneralWidget):
    e_message=None

    def error_popup(self,exception_e):
        error_message = str(exception_e)
        print(error_message)
        self.e_message = ErrorMessage(error_message)
        self.e_message.show()

    def __init__(self,main_widget):
        super().__init__(main_widget)