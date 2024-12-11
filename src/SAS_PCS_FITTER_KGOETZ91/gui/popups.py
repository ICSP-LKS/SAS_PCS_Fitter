from SAS_PCS_FITTER_KGOETZ91.gui.generalgui import GeneralGUI
import numpy as np
import pathlib
from os.path import join, expanduser

from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, Signal
from PySide6.QtWidgets import QFileDialog

from SAS_PCS_FITTER_KGOETZ91.datamodels.oneddata import SAXSData, SANSData, PCSData

class DataLoaderWindow(GeneralGUI):

    updated = Signal()
    saxs_data = None
    sans_data = None
    pcs_data = None

    def _load_saxs_data(self):
        file_name  = QFileDialog.getOpenFileName(self._main_window,"Load SAXS data", expanduser(r"~/"))
        self._widget_list['SAXS_file_label'].setText(file_name[0])
        self.saxs_data = SAXSData().from_file(file_name[0])
        self.updated.emit()

    def _load_sans_data(self):
        file_name  = QFileDialog.getOpenFileName(self._main_window,"Load SAXS data", expanduser(r"~/"))
        self._widget_list['SANS_file_label'].setText(file_name[0])
        self.sans_data = SANSData.from_file(file_name[0])
        self.updated.emit()

    def _load_pcs_data(self):
        file_name  = QFileDialog.getOpenFileName(self._main_window,"Load SAXS data", expanduser(r"~/"))
        self._widget_list['PCS_file_label'].setText(file_name[0])
        self.pcs_data = PCSData.from_file(file_name[0])
        self.updated.emit()

    def _make_connections(self):
        self._widget_list["SAXS_load_button"].clicked.connect(self._load_saxs_data)
        self._widget_list["SANS_load_button"].clicked.connect(self._load_sans_data)
        self._widget_list["PCS_load_button"].clicked.connect(self._load_pcs_data)
        self._widget_list["cancel_button"].clicked.connect(self._main_window.close)

    def __init__(self,parent=None):
        ui_file_name = r"DataLoader.ui"
        path = pathlib.Path(__file__).parent.resolve()
        ui_file = QFile(join(path,ui_file_name))
        loader = QUiLoader()
        widget = loader.load(ui_file,parent)
        ui_file.close()

        super().__init__(widget)
        self._make_connections()
