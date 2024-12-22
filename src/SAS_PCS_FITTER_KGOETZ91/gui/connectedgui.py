import numpy as np
from SAS_PCS_FITTER_KGOETZ91.gui.generalgui import GeneralGUI
from SAS_PCS_FITTER_KGOETZ91.gui.dataloader import DataLoaderWindow
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout
from pyqtgraph import PlotWidget
import pyqtgraph as pg
class ConnectedGUI(GeneralGUI):

    data_updated = Signal()
    saxs_data = None
    sans_data = None
    pcs_data = None

    def _update_plot_data(self):
        if type(self.saxs_data) != type(None):
            self._saxs_plotter.plot(self.saxs_data.x,self.saxs_data.y)
        if type(self.sans_data) != type(None):
            self._sans_plotter.plot(self.sans_data.x,self.sans_data.y)
        if type(self.pcs_data) != type(None):
            self._pcs_plotter.plot(self.pcs_data.x,self.pcs_data.y)

    def _create_popups(self):
        self.data_loader_window = DataLoaderWindow()
        self.data_loader_window.updated.connect(self._get_data_info)

    def _create_plotter(self):
        nulls = np.linspace(0,1000)
        self._saxs_plotter = PlotWidget()
        self._widget_list['saxs_plot_layout'].addWidget(self._saxs_plotter)
        self._saxs_plotter.plot(nulls,nulls)


        self._sans_plotter = PlotWidget()
        self._widget_list['sans_plot_layout'].addWidget(self._sans_plotter)
        self._sans_plotter.plot(nulls,nulls)

        self._pcs_plotter = PlotWidget()
        self._widget_list['pcs_plot_layout'].addWidget(self._pcs_plotter)
        self._pcs_plotter.plot(nulls,nulls)

        self.data_updated.connect(self._update_plot_data)

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
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')
        self._create_popups()
        self._create_plotter()
        self._make_connections()