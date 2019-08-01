import sys
import numpy as np
from PyQt5.QtCore import QByteArray, QDataStream, QIODevice
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.QtNetwork import QHostAddress, QTcpServer


class Server(QDialog):
    def __init__(self):
        super().__init__()
        self.tcpServer = None

    def sessionOpened(self, port=8000):
        self.tcpServer = QTcpServer(self)
        address = QHostAddress('127.0.0.1')
        if not self.tcpServer.listen(address, port):
            print("cant listen!")
            self.close()
            return

        print("Server Ready")
        self.tcpServer.newConnection.connect(self.dealCommunication)

    def dealCommunication(self):
        # Get a QTcpSocket from the QTcpServer
        clientConnection = self.tcpServer.nextPendingConnection()

        # instantiate a QByteArray
        block = QByteArray()

        # QDataStream class provides serialization of binary data to a QIODevice
        out = QDataStream(block, QIODevice.ReadWrite)

        # We are using PyQt5 so set the QDataStream version accordingly.
        out.setVersion(QDataStream.Qt_5_0)
        out.writeUInt16(0)

        # this is the message we will send it could come from a widget.
        message = "ok"

        # get a byte array of the message encoded appropriately.
        message = bytes(message, encoding='ascii')

        # now use the QDataStream and write the byte array to it.
        out.writeString(message)
        out.device().seek(0)
        out.writeUInt16(block.size() - 2)

        # wait until the connection is ready to read
        clientConnection.waitForReadyRead()

        # read incomming data
        instr = clientConnection.readAll()

        # in this case we print to the terminal could update text of a widget if we wanted.
        # data = str(instr, encoding='ascii')
        data = instr
        data = np.frombuffer(data, dtype=np.uint)
        print("Get ", data, " from client")

        # get the connection ready for clean up
        clientConnection.disconnected.connect(clientConnection.deleteLater)

        # now send the QByteArray.
        # clientConnection.write(block)

        # now disconnect connection.
        clientConnection.disconnectFromHost()
        print("Disconnection")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    server = Server()
    server.sessionOpened(PORT=8000)
    sys.exit(server.exec_())
