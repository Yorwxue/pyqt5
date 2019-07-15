# https://stackoverflow.com/questions/46531542/python-sending-signals-between-two-qthreads
import sys
import numpy as np
from PyQt5 import QtWidgets, QtCore

SHOW = True


class AuthWorker(QtCore.QObject):
    authenticate = QtCore.pyqtSignal()

    def __init__(self):
        super(AuthWorker, self).__init__()

    def run(self):
        QtCore.QThread.sleep(1)
        self.authenticate.emit()


class Worker(QtCore.QObject):
    finished = QtCore.pyqtSignal(str)
    authenticator = 5

    def __init__(self, parent=None):
        super(Worker, self).__init__(parent)
        self.auth = AuthWorker()
        self.auth_thread = QtCore.QThread()
        self.auth.moveToThread(self.auth_thread)
        self.auth.authenticate.connect(self.setauthentication)
        self.auth_thread.started.connect(self.auth.run)

    def setauthentication(self):
        self.authenticator = "y"

    def run(self):
        self.auth_thread.start()
        QtCore.QThread.sleep(1)
        self.finished.emit('auth: %s' % self.authenticator)


class Window(QtWidgets.QWidget):
    def __init__(self):
        super(Window, self).__init__()
        self.button = QtWidgets.QPushButton('Test', self)
        self.button.clicked.connect(self.handleButton)
        self.edit = QtWidgets.QLineEdit(self)
        self.edit.setReadOnly(True)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.edit)
        layout.addWidget(self.button)

        # target worker: Worker
        self.worker = self_Worker()

        # if SHOW: print("create thread to execute Worker")
        self.thread = QtCore.QThread()
        self.worker.moveToThread(self.thread)

        # if SHOW: print('"finished" in worker connect to function: handleFinished')
        self.worker.finished.connect(self.handleFinished)

        # if SHOW: print("Worker thread connect to function run in Worker")
        self.thread.started.connect(self.worker.run)

        # if SHOW: print("Window initial complete")

    def handleFinished(self, text):
        if SHOW: print("handleFinished in Window")
        if SHOW: print("Worker quit")
        self.thread.quit()
        self.edit.setText(text)
        if SHOW: print("-----------------------")

    def handleButton(self):
        if SHOW: print("=======================")
        # print("handleButton")
        if not self.thread.isRunning():
            if SHOW: print("thread isn't Running")
            self.edit.clear()
            if SHOW: print("Worker start\n")
            self.thread.start()
        else:
            if SHOW: print("thread is Running")


class self_Worker(QtCore.QObject):
    finished = QtCore.pyqtSignal(str)
    ret_list = np.array([-1, -1, -1])

    def __init__(self, parent=None):
        super(self_Worker, self).__init__(parent)

        # target worker: AuthWorker
        self.auth = self_AuthWorker()

        # if SHOW: print("create thread to execute AuthWorker")
        self.auth_thread = QtCore.QThread()
        self.auth.moveToThread(self.auth_thread)

        # if SHOW: print('"authenticate" in AuthWorker connect to function: setauthentication')
        self.auth.authenticate.connect(self.setauthentication)

        # if SHOW: print("AuthWorker thread connect to function run in AuthWorker")
        self.auth_thread.started.connect(self.auth.run)

        # if SHOW: print("Worker initial complete")

    def setauthentication(self):
        if SHOW: print("setauthentication")
        self.ret_list = np.random.randint(0, 10, (3))
        if SHOW: print("AuthWorker quit")
        self.auth_thread.quit()

    def run(self):
        if SHOW: print("run in Worker")
        if SHOW: print("AuthWorker start\n")
        self.auth_thread.start()
        if SHOW: print("Worker sleep")
        QtCore.QThread.sleep(1)
        if SHOW: print("Worker emit")
        self.finished.emit('auth: %s' % self.ret_list)


class self_AuthWorker(QtCore.QObject):
    authenticate = QtCore.pyqtSignal()

    def __init__(self):
        super(self_AuthWorker, self).__init__()

    def run(self):
        if SHOW: print("run in AuthWorker")
        # print("AuthWorker sleep")
        # QtCore.QThread.sleep(1)
        if SHOW: print("AuthWorker emit")
        self.authenticate.emit()


if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.setGeometry(600, 100, 200, 100)
    window.show()
    sys.exit(app.exec_())
