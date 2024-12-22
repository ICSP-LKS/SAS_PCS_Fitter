from os.path import join, expanduser
import pathlib

from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, Signal
from PySide6.QtWidgets import QFileDialog

from SAS_PCS_FITTER_KGOETZ91.gui.generalgui import GeneralGUI
from SAS_PCS_FITTER_KGOETZ91.datamodels.oneddata import BaseOneDDataSet


class DataTab(GeneralGUI):

    dataset = None
    updated = Signal()

    def _load_data(self):
        try:
            file_name  = QFileDialog.getOpenFileName(self._main_window,"Load SAXS data", expanduser(r"~/"))
            self._widget_list['FileLabel'].setText(file_name[0])
            self.dataset = BaseOneDDataSet().from_file(file_name[0])
            print(self.dataset)
            self.updated.emit(self.dataset)
        except Exception as e:
            self.error_popup(e)

    def _make_connections(self):
        self._widget_list["LoadButton"].clicked.connect(self._load_data)

    def __init__(self,tabname,parent=None):
        self.name = tabname
        ui_file_name = r"DataLoaderTab.ui"
        path = pathlib.Path(__file__).parent.resolve()
        ui_file = QFile(join(path,ui_file_name))
        loader = QUiLoader()
        widget = loader.load(ui_file,parent)
        ui_file.close()

        super().__init__(widget)
        self._make_connections()


class DataLoaderWindow(GeneralGUI):

    updated = Signal()
    data = {'SAXS':None, 'SANS':None, 'PCS':None}

    def _make_connections(self):
        self._widget_list["cancel_button"].clicked.connect(self._main_window.close)
        self._widget_list["apply_button"].clicked.connect(self._print)

    def _print(self):
        print(self.saxs_data)

    def _update_data(self,dataset):
        sender = self.sender()
        if self.data[sender.name]!=sender.dataset:
            self.data[sender.name]=sender.dataset

    def _fill_tabs(self):
        self._saxs_tab = DataTab("SAXS")
        self._sans_tab = DataTab("SANS")
        self._pcs_tab = DataTab("PCS")
        self._widget_list['tabWidget'].addTab(self._saxs_tab._main_window,"SAXS")
        self._widget_list['tabWidget'].addTab(self._sans_tab._main_window,"SANS")
        self._widget_list['tabWidget'].addTab(self._pcs_tab._main_window,"PCS")
        for i in range(self._widget_list['tabWidget'].count):
            self._widget_list['tabWidget'].widget(i).updated.connect(self._update_data)

    def __init__(self,parent=None):
        ui_file_name = r"DataLoader.ui"
        path = pathlib.Path(__file__).parent.resolve()
        ui_file = QFile(join(path,ui_file_name))
        loader = QUiLoader()
        widget = loader.load(ui_file,parent)
        ui_file.close()

        super().__init__(widget)
        self._fill_tabs()
        self._make_connections()
