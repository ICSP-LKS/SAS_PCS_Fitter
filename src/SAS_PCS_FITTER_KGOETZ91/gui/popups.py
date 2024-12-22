from SAS_PCS_FITTER_KGOETZ91.gui.generalwidget import  GeneralWidget
from os.path import join
from tkinter import Tk
import pathlib

from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile

class ErrorMessage(GeneralWidget):

    def _copy_error_message(self):
        r = Tk()
        r.withdraw()
        r.clipboard_clear()
        r.clipboard_append(self._widget_list['error_message'].text())
        r.update()
        r.destroy()

    def _make_connections(self,error_message):
        text = 'The following error occurred:\n\n'+error_message
        self._widget_list['error_message'].setText(text)
        self._widget_list['ok'].clicked.connect(self.destroy)
        self._widget_list['copy'].clicked.connect(self._copy_error_message)

    def __init__(self,error_message='Unknown Error', parent=None):
        ui_file_name = r"ErrorWindow.ui"
        path = pathlib.Path(__file__).parent.resolve()
        ui_file = QFile(join(path,ui_file_name))
        loader = QUiLoader()
        widget = loader.load(ui_file,parent)
        ui_file.close()

        super().__init__(widget)
        self._make_connections(error_message)