from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QFile,QIODevice

from SAS_PCS_FITTER_KGOETZ91.gui.connectedgui import ConnectedGUI

import sys
import pathlib
from os.path import join

class GUI():

    def __init__(self):
        path = pathlib.Path(__file__).parent.resolve()
        ui_file_name = r'MainWindow.ui'
        # Some code to obtain the form file name, ui_file_name
        app = QApplication(sys.argv)
        ui_file = QFile(join(path,ui_file_name))
        if not ui_file.open(QIODevice.ReadOnly):
            print("Cannot open {}: {}".format(ui_file_name, ui_file.errorString()))
            sys.exit(-1)
        loader = QUiLoader()
        widget = ConnectedGUI(loader.load(ui_file, None))
        ui_file.close()
        widget.show()
        sys.exit(app.exec())