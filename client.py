import sys
import zlib
import base64


# from PyQt4.QtCore import *
from PyQt4.QtCore import PYQT_VERSION_STR, QFile, QFileInfo, QSettings, QString, QT_VERSION_STR, QTimer, QVariant, Qt, SIGNAL, QObject, QThread

from PyQt4.QtGui import *
from PyQt4.QtNetwork import *
# from secrets import *


#the worker class here only exists when connection is present.  This is managed by caller
class worker(QObject):
    def __init__(self, handle=0, parent=None):
        super(worker, self).__init__(parent)
        self.add = QHostAddress.LocalHost
        # self.add = '52.193.85.143'
        self.port = 8089

        self.buff = ''
        self.bs = 0
        self.count = 0

        self.pim = QTimer()
        self.pim.timeout.connect(self.ping)
        self.pim.start(3000)

    def ping(self):
        self.send('hi')

    def __del__(self):
        # print 'worker dying'
        pass

    def connected(self):
        self.emit(SIGNAL("connected()"),)

    def work(self):
        self.sock = QTcpSocket(self)
        self.connect(self.sock,SIGNAL("connected()"),self.connected)
        self.connect(self.sock,SIGNAL("disconnected()"),self.disco)
        self.connect(self.sock,SIGNAL("readyRead()"),self.process)
        self.sock.connectToHost(self.add, self.port)
        if not self.sock.waitForConnected(3000): self.disco()

    def send(self, m):
        if (self.sock.state()!=QAbstractSocket.ConnectedState): return

        m = base64.b64encode(zlib.compress(m))

        block = hex(len(m))[2:].zfill(4) + m
        self.sock.writeData(block)
        self.sock.waitForBytesWritten()
        # self.sock.flush()


    def process(self):
        while self.sock.bytesAvailable() > 0:
            self.buff = self.buff + self.sock.readData(2048)
            if self.bs == 0:
                if len(self.buff) < 4: return
                self.bs = int(self.buff[:4],16)
                self.buff = self.buff[4:]
            if self.bs > 0:
                if len(self.buff) < self.bs: return
                out = self.buff[:self.bs]
                self.buff = self.buff[self.bs:]
                self.bs = 0

                out = base64.b64decode(out)
                out = zlib.decompress(out)

                if not out=='hi':
                    self.emit(SIGNAL("recv(PyQt_PyObject)"),out)

    def disco(self):
        self.sock.disconnectFromHost()
        self.emit(SIGNAL("finished()"),)
        pass

    def error(self,x):
        print 'error', x
        self.emit(SIGNAL("error()"),)
        self.emit(SIGNAL("finished()"),)

    def flush(self):
        self.sock.flush()


# caller is a persistent class that manages network connections.
class caller(QObject):
    def __init__(self, parent=None):
        super(caller, self).__init__(parent)
        self.thread = 0
        self.tim = QTimer()
        self.tim.timeout.connect(self.callup)
        self.online = 0

    def __del__(self):
        self.hangup()


    def callup(self):
        self.online = 1
        try:
            if self.thread.isRunning():
                return
        except: pass

        w = worker()
        thread = QThread()
        w.moveToThread(thread)
        thread.w = w
        self.connect(thread,SIGNAL("started()"),w.work)
        self.connect(w,SIGNAL("finished()"),thread.quit)
        self.connect(w,SIGNAL("finished()"),self.disco)
        self.connect(thread,SIGNAL("finished()"),thread.deleteLater)
        self.connect(self,SIGNAL("send(PyQt_PyObject)"),w.send)
        self.connect(w,SIGNAL("recv(PyQt_PyObject)"),self.recv)
        self.connect(self,SIGNAL("hangup()"),w.disco)
        self.connect(w,SIGNAL("connected()"),self.connected)

        self.connect(self,SIGNAL("flusher()"),w.flush)
        thread.start()
        self.thread = thread

    def connected(self):
        self.emit(SIGNAL("connected()"),)
        self.tim.stop()

    def send(self, x):
        self.emit(SIGNAL("send(PyQt_PyObject)"),x)

    def recv(self,x):
        self.emit(SIGNAL("recv(PyQt_PyObject)"),x)

    def hangup(self):
        self.emit(SIGNAL("hangup()"),)
        self.online = 0

    def disco(self):
        self.emit(SIGNAL("disconnected()"),)
        if (self.online==1): self.tim.start(2000)

    def flush(self):
        self.emit(SIGNAL("flusher()"),)



class uclient(QObject):
    def __init__(self, parent=None):
        super(uclient,self).__init__(parent)
        self.sock = QUdpSocket()
        self.sock.bind(8081,QUdpSocket.ShareAddress)
        self.sock.readyRead.connect(self.readdata)

        self.add = QHostAddress.LocalHost
        # self.add = QHostAddress('54.254.170.199')

    def readdata(self):
        while self.sock.hasPendingDatagrams():
            x = self.sock.readDatagram(2048)
            self.emit(SIGNAL("recv(PyQt_PyObject)"),x[0])
            # print 'client got', x[0]

    def send(self, m):
        self.sock.writeDatagram(m, self.add, 8079)
        # print 'client sent', m
