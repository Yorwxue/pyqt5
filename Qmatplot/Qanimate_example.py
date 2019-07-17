from __future__ import unicode_literals
import sys
import os
import numpy as np
import matplotlib
# Make sure that we are using QT5
matplotlib.use('Qt5Agg')
from PyQt5 import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

progname = os.path.basename(sys.argv[0])
progversion = "0.1"


class MatplotCanvas(FigureCanvas):
    """A template for plot object."""

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        self.compute_initial_figure()
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(
            self,
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Expanding
        )
        FigureCanvas.updateGeometry(self)

    def compute_initial_figure(self):
        pass


class StaticMatplotCanvas(MatplotCanvas):
    """Simple canvas with a sine plot."""

    def compute_initial_figure(self):
        t = np.arange(0.0, 3.0, 0.01)
        s = np.sin(2 * np.pi * t)
        self.axes.plot(t, s)


class DynamicMatplotCanvas(MatplotCanvas):
    """A canvas that can updates itself with a new plot."""

    def __init__(self, *args, **kwargs):
        MatplotCanvas.__init__(self, *args, **kwargs)
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.update_figure)
        timer.start(100)
        self.counter = 0
        self.expired_lines = None

    def compute_initial_figure(self):
        self.axes.plot([0, 30], [0, 0], 'r')

    def update_figure(self):
        self.counter += 1
        x = np.linspace(self.counter, self.counter + np.pi * 10, num=100)
        y = np.sin(x)

        # clear the lines drawn last time
        self._clear_plot()

        self.expired_lines = self.axes.plot(x - self.counter, y)
        self.draw()

    def _clear_plot(self):
        try:
            self.axes.lines.remove(self.expired_lines[0])
        except Exception as e:
            print("clear plot error: ", e)
            pass


class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("application main window")

        #  manu setting
        # ===================================================
        self.file_menu = QtWidgets.QMenu('&File', self)
        self.file_menu.addAction('&Quit', self.fileQuit,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        self.menuBar().addMenu(self.file_menu)

        self.help_menu = QtWidgets.QMenu('&Help', self)
        self.menuBar().addSeparator()
        self.menuBar().addMenu(self.help_menu)

        self.help_menu.addAction('&About', self.about)
        # ===================================================

        # layout setting
        # ===================================================
        self.main_widget = QtWidgets.QWidget(self)

        l = QtWidgets.QVBoxLayout(self.main_widget)

        # an example of static plot
        sc = StaticMatplotCanvas(self.main_widget, width=5, height=4, dpi=100)

        # an example of dynamic plot
        dc = DynamicMatplotCanvas(self.main_widget, width=5, height=4, dpi=100)

        # add both plot into window
        l.addWidget(sc)
        l.addWidget(dc)
        # ===================================================

        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

        self.statusBar().showMessage("All hail matplotlib!", 2000)

    def fileQuit(self):
        self.close()

    def closeEvent(self, ce):
        self.fileQuit()

    def about(self):
        QtWidgets.QMessageBox.about(
            self,
            "About",
            """None"""
        )


qApp = QtWidgets.QApplication(sys.argv)

aw = ApplicationWindow()
aw.setWindowTitle("%s" % progname)
aw.show()
sys.exit(qApp.exec_())
#qApp.exec_()