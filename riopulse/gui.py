import sys
import os

from PyQt5 import QtCore, uic
from PyQt5.QtWidgets import QApplication, QWidget

from .pulsegen import PulseGen


def gui(p: PulseGen):
    """Creates a simple GUI for a pulse generator object."""

    # Determines if the app has been run from an ipython console.
    try:
        from IPython import get_ipython
        ip = get_ipython()

        if ip:
            is_ipython = True
            ip.magic('gui qt')
        else:
            is_ipython = False

    except ModuleNotFoundError:
        is_ipython = False

    app = QtCore.QCoreApplication.instance()  # QApplication is a singleton.
    if not app:
        app = QApplication(sys.argv)

    window = QWidget()

    ui_file = os.path.join(os.path.dirname(__file__), 'pulsegen.ui')
    uic.loadUi(ui_file, window)

    window.continueButton.clicked.connect(p.run_continuous)
    window.singleButton.clicked.connect(p.run_single)
    window.stopButton.clicked.connect(p.stop)

    window.show()
    window.activateWindow()

    if is_ipython:
        # The app has been embedded into the ipython even loop already. 
        # The widget window is returned to be accessible from the interactive 
        # console. 
        return window
    else:
        # Executes the app event loop.
        sys.exit(app.exec())