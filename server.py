import sys
import zlib
import base64


# from PyQt4.QtCore import *
from PyQt4.QtCore import PYQT_VERSION_STR, QFile, QFileInfo, QSettings, QString, QT_VERSION_STR, QTimer, QVariant, Qt, SIGNAL, QObject, QThread

# from PyQt4.QtGui import *
from PyQt4.QtNetwork import *



class worker(QObject):
    def __init__(self, handle=0, parent=None):
        super(worker, self).__init__(parent)
        self.handle = handle

        self.buff = ''
        self.bs = 0

        print 'worker alive'


    def __del__(self):
        print 'worker dying'
        self.emit(SIGNAL("stopping(int)"),self.idnum)
        pass

    def work(self):
        self.sock = QTcpSocket(self)
        self.sock.setSocketDescriptor(self.handle)
        self.connect(self.sock,SIGNAL("disconnected()"),self.disco)
        self.connect(self.sock,SIGNAL("readyRead()"),self.process)
        
        self.pim = QTimer()
        self.pim.timeout.connect(self.ping)
        self.pim.start(5000)


    def ping(self):
        self.send('hi',0)


    def send(self, m,idnum):
        if self.idnum != idnum and idnum != 0:
            return

        m = base64.b64encode(zlib.compress(m))

        block = hex(len(m))[2:].zfill(4) + m
        self.sock.writeData(block)
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
                    self.emit(SIGNAL("recv(PyQt_PyObject,PyQt_PyObject)"),out,self.idnum)


    def disco(self):
        self.emit(SIGNAL("finished()"),)
        pass

    # def dosomething(self,x):
    #     print self.idnum, ': ', x
    #     self.send(x)



class server(QTcpServer):
    def __init__(self, parent=None):
        super(server, self).__init__(parent)
        print 'server listening : ', self.listen(QHostAddress.Any,8089)
        self.counter = 0

    def incomingConnection(self, handle):
        w = worker(handle)
        self.counter += 1
        w.idnum = self.counter
        thread = QThread(self)
        w.moveToThread(thread)
        thread.w = w
        self.connect(thread,SIGNAL("started()"),w.work)
        self.connect(w,SIGNAL("finished()"),thread.quit)
        self.connect(thread,SIGNAL("finished()"),thread.deleteLater)
        self.connect(self,SIGNAL("send(PyQt_PyObject,PyQt_PyObject)"),w.send)
        self.connect(w,SIGNAL("recv(PyQt_PyObject,PyQt_PyObject)"),self.recv)
        self.connect(w,SIGNAL("stopping(int)"),self.stopping)
        thread.start()
        self.emit(SIGNAL("starting(int)"),self.counter)

    def recv(self,m,idnum):
        self.emit(SIGNAL("recv(PyQt_PyObject,PyQt_PyObject)"),m,idnum)

    def send(self,m,idnum):
        self.emit(SIGNAL("send(PyQt_PyObject,PyQt_PyObject)"),m,idnum)

    def stopping(self,idnum):
        self.emit(SIGNAL("stopping(int)"),idnum)



class userver(QObject):
    def __init__(self, parent=None):
        super(userver,self).__init__(parent)
        self.sock = QUdpSocket()
        if not self.sock.bind(8079,QUdpSocket.ShareAddress):
            print 'fail'
        self.sock.readyRead.connect(self.readdata)

        self.listeners = {}
        self.tim = QTimer()
        self.tim.timeout.connect(self.checklist)


    def readdata(self):
        while self.sock.hasPendingDatagrams():
            x = self.sock.readDatagram(2048)
            self.emit(SIGNAL("recv(PyQt_PyObject,PyQt_PyObject)"),x[0],x[1])
            self.listeners[x[1]] = QDateTime().currentDateTime().toTime_t()
            # print 'serv got', x[0]
        self.tim.start(10000)


    def send(self, m, add):
        if add ==0:
            for n in self.listeners:
                self.send(m, n)
        else:
            self.sock.writeDatagram(m, add, 8081)
        # print 'serv sent', m



    def checklist(self):
        now = QDateTime().currentDateTime().toTime_t()
        kill = []
        for n in self.listeners:
            dur = self.listeners[n]
            if now - dur > 300:
                kill.append(n)

        for n in kill:
            del self.listeners[n]

        # print self.listeners



# app = QCoreApplication(sys.argv)
# # app = QApplication(sys.argv)
# serv = server(app)
# app.exec_()
