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
try:
	from PyQt4.QtGui import *
	from PyQt4 import QtCore
	from qimage2ndarray import *
except ImportError:
	pass
from math import *
import time
import FileAgent
import urlparse
import numpy as np

global IMGAapp
IMGAapp = None

def getQImg(im):
	if im is None:
		exit(233)
	im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
	im = array2qimage(im)
	return QPixmap.fromImage(im)

def requireQA():
	global IMGAapp
	if IMGAapp is None:
		IMGAapp = QApplication([sys.argv[0]])

class IMGallery(QWidget):

	def __init__(self, data, ind = 0, top_left = (0, 0), size = (1600, 900), cache = True):
		super(IMGallery, self).__init__()
		global IMGAapp
		self.app = IMGAapp
		self.data = data
		self.imgcache = [None] * len(self.data)
		self.size = size
		self.callback = None
		self._cache = cache
		self.__initGUI(ind, top_left, size)

	@property
	def cache(self):
		return self._cache

	@cache.setter
	def cache(self, value):
		if val==False:
			self._cache = False
		else:
			self._cache = True

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

	def __gain(self, ind, udp = False):
		one = self.data[ind]
		if isinstance(one, str):
			rs = urlparse.urlparse(one)
			label = rs.scheme+'://'+rs.netloc+rs.path
			if self._cache:
				if self.imgcache[ind] is None:
					self.imgcache[ind] = FileAgent.getFile(one)
				f = self.imgcache[ind]
			else:
				f = FileAgent.getFile(one)
			im = f.img(refresh = udp)
		elif isinstance(one, np.ndarray):
			label = 'nolabel'
			im = self.data[self.ind]
		elif callable(one):
			label, im = one(ind)
		else:
			label = one.url
			im = one.img(refresh = udp)
		return label, im

	def __adjustStr(self, x):
		mx = max(self.size[0] - 100, 0)>>3
		if len(x)>mx:
			part = (mx - 3) >> 1
			x = x[:part]+'...'+x[-part:]
		return x

	def __adjustImSize(self, im):
		# rate = im.shape[0]*1./im.shape[1]
		mi = 1.
		mi = max(mi, im.shape[1]*1./self.size[0])
		mi = max(mi, im.shape[0]*1./self.size[1])
		return int(im.shape[1]/mi), int(im.shape[0]/mi)
		# return cv2.resize(im, (int(im.shape[1]/mi), int(im.shape[0]/mi)))

	def refresh(self, update = False):
		label, im = self.__gain(self.ind, update)
		self.callback(im, self.ind)
		self.setWindowTitle('IMGallery' + '  -  ' + self.__adjustStr(label))
		im = cv2.resize(im, self.__adjustImSize(im))
		im = getQImg(im)
		self.imgLabel.setPixmap(im)
		self.disButton.setText('%d/%d'%(self.ind, len(self.data)))

	def show(self, callback = None):
		self.callback = callback
		super(IMGallery, self).show()
		self.refresh()
		ret_code = self.app.exec_()
		return ret_code, self

	def S_refresh(self):
		self.refresh(update=True)

	def S_prev(self, d = 1):
		self.ind -= d
		self.ind = max(self.ind, 0)
		self.refresh()

	def S_next(self, d = 1):
		self.ind += d
		self.ind = min(self.ind, len(self.data)-1)
		self.refresh()

	def S_fromhead(self, offset = 0):
		pre = self.__preclick
		self.__preclick = time.time()
		if self.__preclick - pre < 0.5:
			return self.S_fromtail()
		self.ind = offset
		self.refresh()

	def S_fromtail(self, offset = 0):
		self.ind = len(self.data) - 1 - offset
		self.refresh()

	def keyPressEvent(self, e):
		# print e.key()
		# print [(i,QtCore.Qt.__dict__[i]) for i in dir(QtCore.Qt) if i[:4]=='Key_']
		if e.key() == QtCore.Qt.Key_J:
			self.S_prev()
		if e.key() == QtCore.Qt.Key_L:
			self.S_next()
		if e.key() == QtCore.Qt.Key_PageUp or e.key() == QtCore.Qt.Key_I:
			self.S_prev(25)
		if e.key() == QtCore.Qt.Key_PageDown or e.key() == QtCore.Qt.Key_K:
			self.S_next(25)
		if e.key() == QtCore.Qt.Key_Q:
			self.close()
