# -*- coding: utf-8 -*-
"""
Created on Tue Jun 18 10:13:21 2024

@author: klaus
"""

import numpy as np
from PySide6.QtCore import QObject

class GeneralGUI(QObject):
    
    def _empty_widget_list(self, wlist):
        for button in wlist:
            button.setParent(None)
    
    def _extract_children(self, widget):
        """Recursively goes through all Widgets inside widget and returns a
        list of them."""
        result = np.array([])
        for i in widget.children():
            result = np.append(result,self._extract_children(i))
        return np.append(result,widget)
    
    def _extract_widgets(self):
        """Extract all named widgets from the main window. The widgets are
        returned in a dictonary. From there signals and connections can be
        modified."""
        widget_dict = {}
        wlist = self._extract_children(self._main_window)
        for i in wlist:
            try:
                name = (i.objectName())
                widget_dict[name]=i
            except:
                pass
        return widget_dict
    
    def __init__(self, main_widget):
        super().__init__()
        self._main_window = main_widget
        self._widget_list = self._extract_widgets()

    def show(self):
        self._main_window.show()