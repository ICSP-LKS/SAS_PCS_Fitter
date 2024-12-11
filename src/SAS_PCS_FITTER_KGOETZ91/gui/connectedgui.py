import numpy as np
from SAS_PCS_FITTER_KGOETZ91.gui.generalgui import GeneralGUI
from SAS_PCS_FITTER_KGOETZ91.gui.popups import DataLoaderWindow
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout
from pyqtgraph import PlotWidget

class ConnectedGUI(GeneralGUI):

    data_updated = Signal()
    saxs_data = None
    sans_data = None
    pcs_data = None

    def _create_popups(self):
        self.data_loader_window = DataLoaderWindow()
        self.data_loader_window.updated.connect(self._get_data_info)

    def _create_plotter(self):
        nulls = np.linspace(0,1000)
        # self._saxs_plotter = PlotWidget()
        # self._saxs_layout.addWidget(self._saxs_plotter)
        # self._widget_list['saxs_tab'].setLayout(self._saxs_layout)
        # self._saxs_plotter.plot(nulls,nulls)

        self._sans_layout = QHBoxLayout()
        self._sans_plotter = PlotWidget()
        self._sans_layout.addWidget(self._sans_plotter)
        self._widget_list['sans_tab'].setLayout(self._sans_layout)
        self._sans_plotter.plot(nulls,nulls)

        self._pcs_layout = QHBoxLayout()
        self._pcs_plotter = PlotWidget()
        self._pcs_layout.addWidget(self._pcs_plotter)
        self._widget_list['pcs_tab'].setLayout(self._pcs_layout)
        self._pcs_plotter.plot(nulls,nulls)

    def _get_data_info(self):
        saxs_data = self.data_loader_window.saxs_data
        sans_data = self.data_loader_window.sans_data
        pcs_data = self.data_loader_window.pcs_data

        if saxs_data != self.saxs_data:
            self.saxs_data = saxs_data
            self.data_updated.emit()
        if sans_data != self.sans_data:
            self.sans_data = sans_data
            self.data_updated.emit()
        if pcs_data != self.pcs_data:
            self.pcs_data = pcs_data
            self.data_updated.emit()

    def _connect_file_menu(self):
        self._widget_list['actionLoad_Data'].triggered.connect(self.data_loader_window.show)

    def update_plots(self):
        saxs_plotter = self._widget_list[""]

    def _make_connections(self):
        self._connect_file_menu()
        self.data_updated.connect(self.update_plots)

    def __init__(self,main_widget):
        super().__init__(main_widget)
        self._create_popups()
        self._create_plotter()
        self._make_connections()