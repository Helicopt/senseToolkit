#!/usr/bin/python
# -*- coding: utf8 -*-
#########################################################################
# File Name: magic/ImageGallery.py
# Author: Toka
# mail: fengweitao@sensetime.com
# Created Time: 2018年07月29日 星期日 17时30分26秒
#########################################################################
import sys
import cv2
from PyQt4.QtGui import *
from PyQt4 import QtCore
from math import *
from qimage2ndarray import *
import time
import FileAgent

def getQImg(im):
	if im is None:
		exit(233)
	im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
	im = array2qimage(im)
	return QPixmap.fromImage(im)

class IMGallery(QWidget):

	def __init__(self, data, ind = 0, top_left = (0, 0), size = (1600, 900)):
		super(IMGallery, self).__init__()
		self.data = data
		self.size = size
		self.__initGUI(ind, top_left, size)

	def __initGUI(self, ind, top_left, size):
		self.resize(*size)
		self.move(*top_left)
		self.setWindowTitle('IMGallery')

		prevButton = QPushButton('Prev')
		nextButton = QPushButton('Next')
		disButton = QPushButton('/')
		freshButton = QPushButton('Refresh')
		self.prevButton = prevButton
		self.nextButton = nextButton
		self.disButton = disButton
		self.freshButton = freshButton

		self.imgLabel = QLabel()
		# print dir(self.imgLabel)
		self.imgLabel.setMinimumWidth(max(size[0]-40, 0))
		self.imgLabel.setAlignment(QtCore.Qt.AlignVCenter|QtCore.Qt.AlignHCenter)
		self.ind = ind
		self.__preclick = 0

		vbox = QVBoxLayout()
		vbox.addStretch(1)
		vbox.addWidget(disButton)
		vbox.addWidget(prevButton)
		vbox.addWidget(nextButton)
		vbox.addWidget(freshButton)

		hbox = QHBoxLayout()
		# hbox.addStretch(1)
		# hbox.setWidth(1800)
		# print dir(hbox)
		hbox.addWidget(self.imgLabel)
		hbox.addLayout(vbox)

		self.setLayout(hbox)

		self.prevButton.clicked.connect(self.S_prev)
		self.nextButton.clicked.connect(self.S_next)
		self.disButton.clicked.connect(self.S_fromhead)
		self.freshButton.clicked.connect(self.S_refresh)

		return self

	def __gain(self, ind):
		one = self.data[ind]
		if isinstance(one, str):
			label = one
			im = FileAgent.getFile(one).download().img()
		elif isinstance(one, np.ndarray):
			label = 'nolabel'
			im = self.data[self.ind]
		else:
			self.setWindowTitle('IMGallery' + '  -  ' + self.data[self.ind].url)
			im = self.data[self.ind].img()
		return label, im

	def __adjustStr(self, x):
		mx = max(self.size[0] - 100, 0)/30
		if len(x)>mx:
			part = (mx - 3) >> 1
			x = x[:part]+'...'+x[-part:]
		return x

	def __adjustImSize(self, im):
		# rate = im.shape[0]*1./im.shape[1]
		mi = 1.
		mi = max(mi, im.shape[1]*1./self.size[0])
		mi = max(mi, im.shape[0]*1./self.size[1])
		return cv2.resize(im, (im.shape[1]/mi, im.shape[0]/mi))

	def refresh(self):
		label, im = self.__gain(self.ind)
		self.setWindowTitle('IMGallery' + '  -  ' + self.__adjustStr(label))
		im = cv2.resize(im, self.__adjustImSize(im))
		im = getQImg(im)
		self.imgLabel.setPixmap(im)
		self.disButton.setText('%d/%d'%(self.ind, len(self.data)))

	def show(self):
		app = QApplication([sys.argv[0]])
		super(IMGallery, self).show()
		self.refresh()
		ret_code = app.exec_()
		return ret_code, self

	def S_prev(self):
		self.ind -= 1
		self.ind = max(self.ind, 0)
		self.refresh()

	def S_next(self):
		self.ind += 1
		self.ind = min(self.ind, len(self.data)-1)
		self.refresh()

	def S_fromhead(self, offset = 0):
		pre = self.__preclick
		self.__preclick = time.time()
		if self.__preclick - pre < 0.8:
			return self.S_fromtail()
		self.ind = offset
		self.refresh()

	def S_fromtail(self, offset = 0):
		self.ind = len(self.data) - 1 - offset
		self.refresh()

	def keyPressEvent(self, e):
		# print e.key()
		# print [(i,QtCore.Qt.__dict__[i]) for i in dir(QtCore.Qt) if i[:4]=='Key_']
		if e.key() == QtCore.Qt.Key_A or e.key() == QtCore.Qt.Key_W:
			self.S_prev()
		if e.key() == QtCore.Qt.Key_S or e.key() == QtCore.Qt.Key_D:
			self.S_next()
		if e.key() == QtCore.Qt.Key_PageUp:
			for i in range(25):
				self.S_prev()
		if e.key() == QtCore.Qt.Key_PageDown:
			for i in range(25):
				self.S_next()
