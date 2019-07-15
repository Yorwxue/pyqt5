# three layers, two way
# first way:
#     first layer: window (or called main)
#     second layer: Worker
# second way:
#     first layer: window (or called main)
#     two layer: intermedia
#     third layer: AuthWorker
# only using queue to share data
# circulation in both two way

import sys
import numpy as np
from PyQt5 import QtWidgets, QtCore
from queue import Queue


SHOW = True


class Window(QtWidgets.QWidget):
    def __init__(self):
        super(Window, self).__init__()
        # Worker button
        self.worker_button = QtWidgets.QPushButton('Worker', self)
        self.worker_button.clicked.connect(self.worker_handleButton)
        # AuthWorker button
        self.circu_button = QtWidgets.QPushButton('AuthWorker', self)
        self.circu_button.clicked.connect(self.circu_handleButton)
        # generate
        self.gen_button = QtWidgets.QPushButton('Generate', self)
        self.gen_button.clicked.connect(self.gen_handleButton)

        self.edit = QtWidgets.QLineEdit(self)
        self.edit.setReadOnly(True)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.edit)
        layout.addWidget(self.worker_button)
        layout.addWidget(self.circu_button)
        layout.addWidget(self.gen_button)

        self.queue = Queue()
        self.data = np.zeros(3)

        # create thread
        self.thread = QtCore.QThread()
        self.gen_thread = QtCore.QThread()
        self.circu_thread = QtCore.QThread()

        # bind
        # -----------------
        # target worker: Worker
        self.worker = Worker(self.queue)
        self.worker.moveToThread(self.thread)

        # target worker: Worker (generate)
        self.gen_worker = Worker(self.queue)
        self.gen_worker. moveToThread(self.gen_thread)

        # target worker: circulation of workers
        self.circu_worker = intermedia(self.queue)
        self.circu_worker.moveToThread(self.circu_thread)
        # -----------------

        # callback function
        self.worker.finished.connect(self.handleFinished)
        self.gen_worker.finished.connect(self.gen_handleFinished)
        self.circu_worker.finished.connect(self.circu_handleFinished)

    # function 1: worker return
    # -----------------------------------------------
    def handleFinished(self,):
        # if SHOW: print("back to main: Worker")
        self.data = self.queue.get()
        self.thread.quit()
        self.thread.disconnect()
        text = "worker: %s" % self.data
        self.edit.setText(text)
        # self.queue.put(self.data)
        print("main get data: ", self.data, end='')
        print(", queue buffer: %d" % self.queue.qsize())

    def worker_handleButton(self):
        # Worker
        if not self.thread.isRunning():
            self.edit.clear()
            self.thread.started.connect(self.worker.run)
            self.thread.start()
    # -----------------------------------------------

    # function 2: circulation
    # ===============================================
    def circu_handleFinished(self):
        # if SHOW: print("back to main: circulation")
        self.data = self.queue.get()
        self.circu_thread.quit()
        # self.circu_thread.disconnect()
        text = "circulation: %s" % self.data
        self.edit.setText(text)
        print("main get data: ", self.data, end='')
        print(", queue buffer: %d" % self.queue.qsize())

        # restart
        # if not self.circu_thread.isRunning():
        # self.edit.clear()
        self.circu_thread.started.connect(self.circu_worker.circu_run)
        self.circu_thread.start()

    def circu_handleButton(self):
        # intermedia & AuthWorker
        if self.queue.empty():
            self.queue.put(self.data)
        if not self.circu_thread.isRunning():
            self.edit.clear()
            self.circu_thread.started.connect(self.circu_worker.circu_run)
            self.circu_thread.start()
    # ===============================================

    # generate new data for function 2, but still affect function 1
    # -----------------------------------------------
    def gen_handleFinished(self):
        if SHOW: print("back to main: generation")
        self.data = self.queue.get()

        self.gen_thread.quit()
        self.gen_thread.disconnect()

        text = "generate: %s" % self.data
        self.edit.setText(text)
        self.data = self.queue.put(self.data)
        print("queue buffer: %d" % self.queue.qsize())
        # self.gen_thread.start()

    def gen_handleButton(self):
        if not self.gen_thread.isRunning():
            self.edit.clear()
            self.gen_thread.started.connect(self.gen_worker.generate)
            self.gen_thread.start()
    # -----------------------------------------------


class Worker(QtCore.QObject):
    data = np.array([-1, -1, -1])
    finished = QtCore.pyqtSignal()

    def __init__(self, queue, parent=None):
        super(Worker, self).__init__(parent)
        self.queue = queue

    def create_data(self):
        self.data = np.random.randint(0, 100, (3))

    def generate(self):
        while True:
            self.create_data()
            print("Generate new data to queue: ", self.data, end="")
            self.queue.put(self.data)
            print(", queue buffer: %d" % self.queue.qsize())
            QtCore.QThread.sleep(3)
        self.finished.emit()

    def setauthentication(self):
        if SHOW:
            print("back to Worker")
            self.data = self.queue.get()
            print("Worker: get data from queue: ", self.data, end="")
            print(", queue buffer: %d" % self.queue.qsize())
            print("Worker: put data into queue, and emit")
            self.queue.put(self.data)

        self.inter_thread.quit()

        self.finished.emit()

    def run(self):
        # main -> Worker -> main
        # if SHOW: print("run in Worker")
        self.create_data()
        self.queue.put(self.data)
        self.finished.emit()


class intermedia(QtCore.QObject):
    data = np.zeros(3)
    finished = QtCore.pyqtSignal()

    def __init__(self, queue):
        super(intermedia, self).__init__()
        self.queue = queue
        self.self_send_queue = Queue()
        self.self_receive_queue = Queue()
        # AuthWorker
        self.auth = AuthWorker(self.self_send_queue, self.self_receive_queue)
        self.auth_thread = QtCore.QThread()
        self.auth_thread.started.connect(self.auth.run)
        self.auth.finished.connect(self.callback)

    def modified_data(self):
        self.data = self.data + 1

    def circu_run(self):
        # if SHOW: print("run in intermedia")
        # if not self.queue.empty():
        self.data = self.queue.get()
        print("intermedia: get data from queue: ", self.data, end="")
        print(", queue buffer: %d" % self.queue.qsize())

        # +1
        self.modified_data()

        # print("intermedia: put data to queue: ", self.data)
        self.self_send_queue.put(self.data)

        # start AuthWorker
        self.auth_thread.start()

    def callback(self):
        # if SHOW: print("back to intermedia")
        self.queue.put(self.self_receive_queue.get())
        print(", queue buffer: %d" % self.queue.qsize())
        self.auth_thread.quit()
        self.finished.emit()


class AuthWorker(QtCore.QObject):
    data = np.zeros(3)
    finished = QtCore.pyqtSignal()

    def __init__(self, self_receive_queue, self_send_queue):
        super(AuthWorker, self).__init__()
        self.self_receive_queue = self_receive_queue
        self.self_send_queue = self_send_queue

    def modified_data(self):
        self.data = self.data + 1

    def run(self):
        # if SHOW: print("run in AuthWorker")
        if not self.self_receive_queue.empty():
            self.data = self.self_receive_queue.get()
            # print("AuthWorker: get data from queue: ", self.data)

        self.modified_data()

        print("AuthWorker: put data to queue: ", self.data, end="")
        self.self_send_queue.put(self.data)
        self.finished.emit()


if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.setGeometry(600, 100, 200, 100)
    window.show()
    sys.exit(app.exec_())
