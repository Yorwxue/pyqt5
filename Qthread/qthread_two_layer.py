import sys
import numpy as np
from PyQt5 import QtWidgets, QtCore
from queue import Queue


SHOW = False


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
        # Worker button
        self.worker_button = QtWidgets.QPushButton('Worker', self)
        self.worker_button.clicked.connect(self.worker_handleButton)
        # AuthWorker button
        self.auth_button = QtWidgets.QPushButton('AuthWorker', self)
        self.auth_button.clicked.connect(self.auth_handleButton)

        self.edit = QtWidgets.QLineEdit(self)
        self.edit.setReadOnly(True)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.edit)
        layout.addWidget(self.worker_button)
        layout.addWidget(self.auth_button)

        # create thread
        self.thread = QtCore.QThread()

        # target worker: Worker
        self.worker = self_Worker()
        self.worker.moveToThread(self.thread)

        # get return value
        self.worker.finished.connect(self.handleFinished)

    def handleFinished(self, text):
        self.thread.quit()
        self.thread.disconnect()
        self.edit.setText(text)

    def worker_handleButton(self):
        # Worker
        if not self.thread.isRunning():
            self.edit.clear()
            self.thread.started.connect(self.worker.run)
            self.thread.start()

    def auth_handleButton(self):
        # Worker & AuthWorker
        if not self.thread.isRunning():
            self.edit.clear()
            self.thread.started.connect(self.worker.auth_run)
            self.thread.start()


class self_Worker(QtCore.QObject):
    data = np.array([-1, -1, -1])
    finished = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super(self_Worker, self).__init__(parent)
        self.queue = Queue()
        self.auth = self_AuthWorker(self.queue)
        self.auth_thread = QtCore.QThread()
        self.auth_thread.started.connect(self.auth.run)
        self.auth.finished.connect(self.setauthentication)

    def create_data(self):
        self.data = np.random.randint(0, 10, (3))

    def _format_change(self, data):
        data = data.replace('[ ', '').replace('[', '').replace(']', '').replace('  ', ' ').split(' ')
        while ' ' in data:
            index = data.index(' ')
            data.pop(index)
        print("to list: ", data)
        data = np.asarray([int(i) for i in data])
        print("changed type: ", data, type(data))
        return data

    def setauthentication(self, data):
        self.data = data
        self.auth_thread.quit()
        print("get data from AuthWorker: %s, type: %s" %(self.data, type(self.data)))
        self.data = self._format_change(self.data)

    def run(self):
        # main -> Worker -> main
        print("run in Worker")
        self.create_data()
        self.finished.emit("worker: %s" % self.data)

    # main -> Worker -> AuthWorker -> Worker -> main
    def auth_run(self):
        self.queue.put(self.data)
        self.auth_thread.start()
        QtCore.QThread.sleep(1)  # wait for AuthWorker
        self.finished.emit("worker: %s" % self.data)


class self_AuthWorker(QtCore.QObject):
    data = np.zeros(3)
    finished = QtCore.pyqtSignal(str)

    def __init__(self, queue):
        super(self_AuthWorker, self).__init__()
        self.queue = queue

    def modified_data(self):
        self.data = self.data + 1

    def run(self):
        print("run in AuthWorker")
        if not self.queue.empty():
            self.data = self.queue.get()
            print("get data from Worker: %s, type: %s" % (self.data, type(self.data)))
        self.modified_data()
        print("send data to Worker: %s, type: %s" % (str(self.data), type(str(self.data))))
        self.finished.emit(str(self.data))


if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.setGeometry(600, 100, 200, 100)
    window.show()
    sys.exit(app.exec_())
