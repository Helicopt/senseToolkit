#!/usr/bin/python
# -*- coding: utf8 -*-
#########################################################################
# File Name: magic/ImageGallery.py
# Author: Toka
# mail: fengweitao@sensetime.com
# Created Time: 2018年07月29日 星期日 17时30分26秒
#########################################################################
import six
import sys
import cv2

try:
    from PyQt5.QtGui import *
    from PyQt5.QtWidgets import *
    from PyQt5 import QtCore
    from qimage2ndarray import *
except ImportError:
    pass

if six.PY2:
    from urlparse import urlparse
elif six.PY3:
    from urllib.parse import urlparse

from math import *
import time
from time import sleep
from . import FileAgent
# import FileAgent
import threading
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

class cacheWorker(threading.Thread):

    def __init__(self, ctx):
        super(cacheWorker, self).__init__()
        self.ctx = ctx
        self.n = len(ctx.data)
        self.pre = -1
        self.lock = threading.Lock()

    def run(self):
        ctx = self.ctx
        while True:
            # print('worker %s %d'%(ctx.cache, ctx.ind))
            if ctx.cache:
                be = max(ctx.ind - 50, 0)
                en = min(ctx.ind + 51, self.n)
                self.lock.acquire()
                for i in range(be):
                    ctx.imgcache[i] = None, None
                for i in range(en, self.n):
                    ctx.imgcache[i] = None, None
                self.lock.release()
                if ctx.ind!=self.pre:
                    for i in range(be, en):
                        _, one = ctx.imgcache[i]
                        if one is None:
                            udp = True
                            self.lock.acquire()
                            one = ctx.data[i]
                            if isinstance(one, str):
                                rs = urlparse(one)
                                label = rs.scheme+'://'+rs.netloc+rs.path
                                if ctx._cache:
                                    if ctx.imgcache[i][1] is None:
                                        try:
                                            ctx.imgcache[i] = label, FileAgent.getFile(one)
                                        except:
                                            sys.stderr.write('[failed] get %s error.\n'%label)
                                            continue
                                    _, f = ctx.imgcache[i]
                                else:
                                    try:
                                        f = FileAgent.getFile(one)
                                    except:
                                        sys.stderr.write('[failed] get %s error.\n'%label)
                                        continue
                                im = f.img(refresh = udp)
                            elif isinstance(one, np.ndarray):
                                label = 'nolabel'
                                im = one
                                if ctx._cache:
                                    ctx.imgcache[i] = label, im
                            elif callable(one):
                                label, im = one(i)
                                if ctx._cache:
                                    ctx.imgcache[i] = label, im
                            else:
                                label = one.url
                                im = one.img(refresh = udp)
                                if ctx._cache:
                                    ctx.imgcache[i] = label, im
                            # ctx.imgcache[i] = label, one
                            self.lock.release()
                    self.pre = ctx.ind
                else:
                    sleep(1)
            else:
                break


class IMGallery(QWidget):

    E_REFRESH = 1
    E_HOVER = 2
    E_MPRESS = 3
    E_MRELEASE = 4

    def __init__(self, data, ind = 0, top_left = (0, 0), size = (1600, 900), cache = True):
        super(IMGallery, self).__init__()
        global IMGAapp
        self.app = IMGAapp
        self.data = data
        self.imgcache = [(None, None)] * len(self.data)
        self.size = size
        self.callback = None
        self._cache = False
        self.__initGUI(ind, top_left, size)
        self.cache = cache

    @property
    def cache(self):
        return self._cache

    @cache.setter
    def cache(self, value):
        if value==self._cache:
            return
        if value==False:
            self._cache = False
        else:
            self._cache = True
            self.cacheThread = cacheWorker(self)
            if self._cache:
                self.cacheThread.setDaemon(True)
                self.cacheThread.start()

    def renewPosBar(self, x, y, ox, oy, etype):
        content = 'POS:\n%d %d\n\nORIGIN_POS:\n%d %d\n\nLAST_POS:\n%d %d\n\nW: %d, H: %d'\
        %(x, y, ox, oy, self.pcx, self.pcy, ox - self.pcx, oy - self.pcy)
        if etype==IMGallery.E_MPRESS:
            self.pcx = ox
            self.pcy = oy
        self.posBar.setText(content)

    def __initGUI(self, ind, top_left, size):
        self.resize(*size)
        self.move(*top_left)
        self.setWindowTitle('IMGallery')

        prevButton = QPushButton('Prev')
        nextButton = QPushButton('Next')
        disButton = QPushButton('/')
        freshButton = QPushButton('Refresh')
        collapseButton = QPushButton('Collapse')
        infoPan = QTextEdit()
        posBar = QLabel()
        self.prevButton = prevButton
        self.nextButton = nextButton
        self.disButton = disButton
        self.freshButton = freshButton
        self.collapseButton = collapseButton
        self.infoPanel = infoPan
        self.posBar = posBar

        self.imgLabel = QLabel()
        # print dir(self.imgLabel)
        self.imgLabel.setMinimumWidth(max(self.size[0] - max(size[0]/5, 120), 0))
        self.imgLabel.setAlignment(QtCore.Qt.AlignVCenter|QtCore.Qt.AlignHCenter)
        self.ind = ind
        self.__preclick = 0
        self.pcx = 0
        self.pcy = 0
        self.last_scale = 1.
        self.img_size = (0, 0)
        self.infoStatus = True

        infoPan.setMinimumHeight(self.size[1]/2)
        infoPan.setMinimumWidth(self.size[0]/5)
        infoPan.setReadOnly(True)

        vbox = QVBoxLayout()
        subvb = QVBoxLayout()
        subvb.addWidget(infoPan)

        posBar.setText('- -')
        posBar.setMinimumWidth(120)

        vbox.addLayout(subvb)
        vbox.addWidget(collapseButton)
        vbox.addStretch(1)
        vbox.addWidget(posBar)
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

        hbox.setStretch(0,1)
        self.setLayout(hbox)

        self.navi = vbox

        self.prevButton.clicked.connect(self.S_prev)
        self.nextButton.clicked.connect(self.S_next)
        self.disButton.clicked.connect(self.S_fromhead)
        self.freshButton.clicked.connect(self.S_refresh)
        self.collapseButton.clicked.connect(self.S_collapse)

        # print(dir(self.imgLabel))
        def gen_me(tp):
            def mme(e):
                # print(dir(e))
                # print self.imgLabel.width(), self.img_size[0], self.imgLabel.height(), self.img_size[1]
                px = e.x() - (self.imgLabel.width() - self.img_size[0])//2
                py = e.y() - (self.imgLabel.height() - self.img_size[1])//2
                xx = int(px*self.last_scale)
                yy = int(py*self.last_scale)
                self.renewPosBar(px, py, xx, yy, tp)
                if callable(self.callback):
                    self.callback(None, self.ind, type=tp, info = infoPan,
                        x = px, y = py,
                        origin_x = xx, origin_y = yy)
            return mme
        self.imgLabel.setMouseTracking(True)
        self.imgLabel.mouseMoveEvent = gen_me(IMGallery.E_HOVER)
        self.imgLabel.mousePressEvent = gen_me(IMGallery.E_MPRESS)
        self.imgLabel.mouseReleaseEvent = gen_me(IMGallery.E_MRELEASE)

        return self

    def __gain(self, ind, udp = False):
        im = None
        if self._cache and not udp:
            label, im = self.imgcache[ind]
            if hasattr(im, 'img'):
                im = im.img(refresh = False)
        if im is None:
            if self._cache:
                self.cacheThread.lock.acquire()
            one = self.data[ind]
            if isinstance(one, str):
                rs = urlparse(one)
                label = rs.scheme+'://'+rs.netloc+rs.path
                if self._cache:
                    if self.imgcache[ind][1] is None:
                        self.imgcache[ind] = label, FileAgent.getFile(one)
                    _, f = self.imgcache[ind]
                else:
                    f = FileAgent.getFile(one)
                im = f.img(refresh = udp)
            elif isinstance(one, np.ndarray):
                label = 'nolabel'
                im = one
                if self._cache:
                    self.imgcache[ind] = label, im
            elif callable(one):
                label, im = one(ind)
                if self._cache:
                    self.imgcache[ind] = label, im
            else:
                label = one.url
                im = one.img(refresh = udp)
                if self._cache:
                    self.imgcache[ind] = label, im
            if self._cache:
                self.cacheThread.lock.release()
        return label, im.copy() if self._cache else im

    def __adjustStr(self, x):
        mx = max(self.size[0] - 100, 0)>>3
        if len(x)>mx:
            part = (mx - 3) >> 1
            x = x[:part]+'...'+x[-part:]
        return x

    def __adjustImSize(self, im):
        # rate = im.shape[0]*1./im.shape[1]
        mi = 1.
        mi = max(mi, im.shape[1]*1./self.imgLabel.width())
        mi = max(mi, im.shape[0]*1./self.imgLabel.height())
        self.last_scale = mi
        return int(im.shape[1]/mi), int(im.shape[0]/mi)
        # return cv2.resize(im, (int(im.shape[1]/mi), int(im.shape[0]/mi)))

    def refresh(self, update = False):
        self.setFocus()
        label, im = self.__gain(self.ind, update)
        if callable(self.callback):
            self.callback(im, self.ind, type=IMGallery.E_REFRESH, info=self.infoPanel)
        self.setWindowTitle('IMGallery' + '  -  ' + self.__adjustStr(label))
        self.img_size = self.__adjustImSize(im)
        im = cv2.resize(im, self.img_size)
        im = getQImg(im)
        self.imgLabel.setPixmap(im)
        self.disButton.setText('%d/%d'%(self.ind+1, len(self.data)))

    def show(self, callback = None):
        self.callback = callback
        super(IMGallery, self).show()
        self.refresh()
        ret_code = self.app.exec_()
        return ret_code, self

    def S_refresh(self):
        self.refresh(update=True)

    def S_prev(self, *args, **kwargs):
        if 'd' not in kwargs:
            d = 1
        else:
            d = kwargs['d']
        self.ind -= d
        self.ind = max(self.ind, 0)
        self.refresh()

    def S_next(self, *args, **kwargs):
        if 'd' not in kwargs:
            d = 1
        else:
            d = kwargs['d']
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

    def S_collapse(self, *args, **kwargs):
        status = kwargs['status'] if 'status' in kwargs else None
        if status==None:
            self.infoStatus = not self.infoStatus
        else:
            self.infoStatus = status
        if self.infoStatus:
            self.infoPanel.show()
            self.imgLabel.setMinimumWidth(max(self.size[0] - max(self.size[0]/5, 120), 0))
            self.collapseButton.setText('Collapse')
        else:
            self.infoPanel.hide()
            self.imgLabel.setMinimumWidth(max(self.size[0] - 120, 0))
            self.collapseButton.setText('Extend')
        self.resize(0,0)
        self.resize(*self.size)
        self.refresh()

    def keyPressEvent(self, e):
        # print e.key()
        # print [(i,QtCore.Qt.__dict__[i]) for i in dir(QtCore.Qt) if i[:4]=='Key_']
        if e.key() == QtCore.Qt.Key_J or e.key() == QtCore.Qt.Key_Left or e.key() == QtCore.Qt.Key_Up:
            self.S_prev()
        if e.key() == QtCore.Qt.Key_L or e.key() == QtCore.Qt.Key_Right or e.key() == QtCore.Qt.Key_Down:
            self.S_next()
        if e.key() == QtCore.Qt.Key_PageUp or e.key() == QtCore.Qt.Key_I:
            self.S_prev(d=25)
        if e.key() == QtCore.Qt.Key_PageDown or e.key() == QtCore.Qt.Key_K:
            self.S_next(d=25)
        if e.key() == QtCore.Qt.Key_Q:
            self.close()
        if e.key() == QtCore.Qt.Key_Q and (e.modifiers() == QtCore.Qt.ControlModifier):
            exit()

    def __del__(self):
        self.cache = False
        del self.cacheThread

if __name__=='__main__':
    requireQA()
    IMGallery([np.zeros((1080,1920,3), dtype='uint8')]*10).show()
