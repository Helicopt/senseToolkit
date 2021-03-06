#!/usr/bin/python
# -*- coding: utf8 -*-
#########################################################################
# File Name: magic/FileAgent.py
# Author: Toka
# mail: fengweitao@sensetime.com
# Created Time: 2018年07月29日 星期日 18时54分08秒
#########################################################################
import six
if six.PY2:
    import httplib
    from urlparse import urlparse
elif six.PY3:
    import http.client as httplib
    from urllib.parse import urlparse
import ftplib
import os
import cv2
from re import *
from copy import copy
import tempfile
import time
from threading import Lock

img_exts = ['png', 'jpg', 'jpeg', 'bmp', 'tiff']


class quickFtpCon(object):

    funcs = ['__init__', '__getattribute__', 'connect', 'clear_buffer',
             'cb_buffer', 'get_buffer', '__dict__']

    def __init__(self, ip_, port_=0, usn_='anonymous', pwd_='', secure_=False):
        self.ip = ip_
        self.port = port_
        self.usn = usn_
        self.passwd = pwd_
        self.secure_ = secure_
        if secure_:
            self.con = ftplib.FTP_TLS()
        else:
            self.con = ftplib.FTP()
        self.buffer_ = []

    def __getattribute__(self, x):
        if x == 'funcs' or x in quickFtpCon.funcs or x in self.__dict__:
            return super(quickFtpCon, self).__getattribute__(x)
        return getattr(self.con, x)

    def connect(self, usn=None, pwd=None):
        # print self.ip, type(self.port), self.port, self.usn, self.passwd
        if self.port > 1023 and self.port < 65536:
            self.con.connect(self.ip, self.port)
        else:
            self.con.connect(self.ip)
        if usn is not None and pwd is not None:
            self.usn, self.passwd = usn, pwd
        self.con.login(self.usn, self.passwd)
        if self.secure_:
            self.con.prot_p()
        return self

    def clear_buffer(self):
        self.buffer_ = []

    def cb_buffer(self, x):
        self.buffer_.append(x)

    def get_buffer(self):
        return copy(self.buffer_)


class ftpFile(object):
    """descript a ftp file"""

    def __init__(self, con, url='/', parent=None):
        super(ftpFile, self).__init__()
        while len(url) and url[-1] == '/':
            url = url[:-1]
        self.url = url
        self.con = con
        self.__parent = parent
        self.lock = Lock()
        self.__im = None
        self.__fn = None
        self.refresh()

    def refresh(self):
        self.lock.acquire()
        try:
            pwd = self.con.pwd()
            self.con.cwd(self.url)
            self.con.cwd(pwd)
            self.FileStr = ''

            def parseFileLineDir(x):
                # print split('[ \t\n\r]+', x)
                # print '? ', x, '@%s@%s@'%(split('[ \t\n\r]+', x)[-1], self.url.split('/')[-1])
                if split('[ \t\n\r]+', x)[-1] == self.url.split('/')[-1]:
                    self.FileStr = x
                    # print x
            self.con.retrlines('LIST %s/..' % self.url, parseFileLineDir)
            if self.FileStr == '':
                raise Exception('No permission for path: %s' % self.url)
            arr = split('[ \t\n\r]+', self.FileStr)
            self.__mod = arr[0]
            self.__size = int(arr[4])
            self.__time = arr[5]+' '+arr[6]+' '+arr[7]
        except(ftplib.error_perm) as e:
            self.FileStr = ''

            def parseFileLine(x):
                self.FileStr = x
            self.con.retrlines('LIST %s' % self.url, parseFileLine)
            if self.FileStr == '':
                raise Exception('No permission for path: %s' % self.url)
            arr = split('[ \t\n\r]+', self.FileStr)
            self.__mod = arr[0]
            self.__size = int(arr[4])
            self.__time = arr[5]+' '+arr[6]+' '+arr[7]
        self.lock.release()

    def is_dir(self):
        return self.__mod[0] == 'd'

    def is_file(self):
        return self.__mod[0] == '-'

    def size(self):
        return self.__size

    def mode(self):
        return self.__mod

    def modified(self):
        return self.__time

    def is_img(self):
        return split('\.', self.url)[-1].lower() in img_exts and self.is_file()

    def list(self):
        self.lock.acquire()
        if self.is_dir() and self.canRead() and self.canExec():
            sub = []
            self.con.clear_buffer()
            ls = self.con.retrlines('LIST %s' % self.url, self.con.cb_buffer)
            lines = self.con.get_buffer()
            for i in lines:
                arr = split('[ \t\n\r]+', i)
                mod = arr[0]
                url = arr[-1]
                if self.url[-1] == '/':
                    url = self.url + url
                else:
                    url = self.url + '/' + url
                nf = ftpFile(self.con, url, parent=self)
                sub.append(nf)
            return sub
        else:
            raise Exception('cannot list: '
                            + 'not directory ' if not self.is_dir() else ''
                            + 'no permission ' if not self.canRead() else ''
                            + 'cannot enter ' if not self.canExec() else '')
        self.lock.release()

    def canRead(self, admin=True):
        return self.__mod[1] == 'r' and admin or self.__mod[7] == 'r'

    def canWrite(self, admin=True):
        return self.__mod[2] == 'w' and admin or self.__mod[8] == 'w'

    def canExec(self, admin=True):
        return self.__mod[3] == 'x' and admin or self.__mod[9] == 'x'

    def release_tmp(self):
        if self.__fn is not None:
            try:
                if os.path.isfile(self.__fn):
                    # os.system('rm %s' % self.__fn)
                    os.remove(self.__fn)
            except Exception as e:
                pass

    # def __transfer(self):
    # 	self.fd.write()

    @staticmethod
    def createTmpFile(item=None):
        fd, fn = tempfile.mkstemp()
        # print fd, fn
        if item is not None:
            item.__fn = fn
        return os.fdopen(fd, 'wb'), fn

    @staticmethod
    def __transfer(fd):
        def cb(x):
            fd.write(x)
            fd.flush()
        return cb

    def download(self, fd=None):
        self.lock.acquire()
        if self.is_file():
            if fd is None:
                if self.__fn is None:
                    fd, fn = ftpFile.createTmpFile(self)
                else:
                    fd = open(self.__fn, 'wb')
            self.con.retrbinary('RETR %s' % self.url, ftpFile.__transfer(fd))
            fd.close()
        self.lock.release
        return self

    def __str__(self):
        return self.__mod + ' ' + self.url

    def parent(self):
        return self.__parent

    def img(self, refresh=False):
        if self.is_img():
            if self.__im is None or refresh:
                if self.__fn is None or refresh:
                    self.download()
                self.__im = cv2.imread(self.__fn)
        return self.__im

    def __del__(self):
        self.release_tmp()


class httpFile(object):

    def __init__(self, url, timeout=10):
        rs = urlparse(url)
        self.host = rs.netloc
        self.path = rs.path
        self.url = rs.path+'?'+rs.query+'#'+rs.fragment
        self.lock = Lock()
        # print self.url
        self.__fn = None
        self.__im = None
        self.conn = httplib.HTTPConnection(self.host, timeout=timeout)

    @staticmethod
    def createTmpFile(item=None):
        fd, fn = tempfile.mkstemp()
        # print fd, fn
        if item is not None:
            item.__fn = fn
        return os.fdopen(fd, 'wb'), fn

    def download(self, fd=None):
        self.lock.acquire()
        # print dir(self.conn)
        h = self.conn
        h.request('GET', self.url)
        receive = h.getresponse()
        errcode, errmsg = receive.status, receive.reason
        # print errcode, errmsg, headers
        if errcode != 200:
            raise IOError('Connection to %s refused. [%d] %s' % (
                self.host, errcode, errmsg))
        receive = receive.read()
        if fd is None:
            if self.__fn is None:
                fd, fn = httpFile.createTmpFile(self)
            else:
                fd = open(self.__fn, 'wb')
        fd.write(receive)
        fd.close()
        self.lock.release()
        return self

    def release_tmp(self):
        if self.__fn is not None:
            try:
                if os.path.isfile(self.__fn):
                    # os.system('rm %s' % self.__fn)
                    os.remove(self.__fn)
                self.__fn = None
            except Exception as e:
                pass

    def img(self, refresh=False):
        if self.__im is None or refresh:
            if self.__fn is None or refresh:
                self.download()
            self.__im = cv2.imread(self.__fn)
        return self.__im

    def release(self):
        self.release_tmp()

    def __del__(self):
        self.release()
        self.conn.close()


class localFile(object):

    def __init__(self, path):
        self.path = path
        self.__im = None

    def download(self, fd=None):
        return self

    def img(self, refresh=False):
        if self.__im is None or refresh:
            self.__im = cv2.imread(self.path)
        im = self.__im
        if im is None:
            raise IOError('No such file or directory: %s' % self.path)
        return im


def suitFtp(x):
    return x.strip()[:3] == 'ftp'


def suitHttp(x):
    return x.strip()[:4] == 'http'


def parse4Ftp(x):
    urlres = urlparse(x)
    # print urlres
    # print urlres.scheme
    # print urlres.netloc
    # print urlres.path
    # print urlres.query
    # print urlres.fragment
    netloc = urlres.netloc.split(':')
    ip = netloc[0]
    port = 0
    if len(netloc) > 1:
        port = int(netloc[1])
    return ftpFile(quickFtpCon(ip, port).connect(urlres.query, urlres.fragment), urlres.path)


def parse4Http(x):
    return httpFile(x)


def parse4Local(x):
    return localFile(x)


def getFile(x):
    if suitFtp(x):
        return parse4Ftp(x)
    elif suitHttp(x):
        return parse4Http(x)
    else:
        return parse4Local(x)


__all__ = ['getFile', 'parse4Local', 'parse4Ftp', 'parse4Http',
           'suitHttp', 'suitFtp', 'httpFile', 'ftpFile',
           'localFile', 'quickFtpCon']

# if __name__=='__main__':
# 	fn = 'ftp://10.1.30.165:2121/motmetrics/mot.py'
# 	ftp = parse4Ftp(fn)
# 	# map(ftplib.print_line, ftp.list())
# 	print ftp.mode()

# if __name__=='__main__':
# 	con = quickFtpCon('10.1.30.165', '2121').connect()
# 	print dir(con)
# 	print dir(quickFtpCon)
# 	print hasattr(con, 'clear_buffer')
# 	print hasattr(quickFtpCon, 'clear_buffer')
# 	# a = con.retrlines('MLSD mt.py')

# 	# print help(con)
# 	f = ftpFile(con, '/motmetrics/')
# 	print f.is_dir()
# 	print f.is_file()
# 	print f.mode()
# 	print f.size()
# 	print f.modified()
# 	if f.is_dir():
# 		for one in f.list():
# 			print one


# if __name__=='__main__':
# 	htp = httpFile('https://www.baidu.com/img/bd_logo1.png?where=super')
# 	im = htp.img()
# 	cv2.imshow('', im)
# 	cv2.waitKey(0)
