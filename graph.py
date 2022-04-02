import sys
import json
import base64
import sqlite3 as lite
import zlib
from PyQt4.QtCore import *
from PyQt4.QtGui import *


from PyQt4.QtNetwork import *
import client
import time



class viewer(QWidget):
	def __init__(self, parent=None):
		super(viewer, self).__init__(parent)
		self.setFont(QFont('Helvetica', 20))

		layout = QVBoxLayout()
		self.setLayout(layout)

		self.list = QListWidget()
		self.line = QLineEdit()

		self.connect(self.line,SIGNAL("returnPressed()"),self.sender)

		layout.addWidget(self.list)
		layout.addWidget(self.line)
		self.caller = client.uclient()
		self.connect(self.caller,SIGNAL("recv(PyQt_PyObject)"),self.getter)

		self.tim = QTimer()
		self.tim.setSingleShot(1)
		self.connect(self.tim,SIGNAL("timeout()"),self.timeout)

		self.reclist = []


	def sender(self):
		t = self.line.text()
		self.line.clear()
		sock = QUdpSocket()
		sock.writeDatagram(t, QHostAddress.LocalHost, 8081)
		print t

	def getter(self,m):
		print str(time.time()) + ' : ' + str(m)
		if not m in self.reclist:
			self.list.insertItem(0,m)
			self.reclist.append(m)
		self.tim.start(500)

	def timeout(self):
		self.reclist = []
		self.list.clear()

class mainwin(QMainWindow):
	def __init__(self, parent=None):
		super(mainwin, self).__init__(parent)
		frame = QFrame()
		self.setCentralWidget(frame)
		layout = QVBoxLayout()
		frame.setLayout(layout)

		self.setWindowTitle('Viewer')
		self.resize(800,600)

		t = viewer()
		layout.addWidget(t)

		# layout.setContentsMargins(0,0,0,0)
		# self.showFullScreen()
		# self.showMaximized()









app = QApplication(sys.argv)
form = mainwin()
form.show()
form.raise_()


app.exec_()
