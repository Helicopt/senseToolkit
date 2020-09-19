#!/usr/bin/python
# -*- coding: utf8 -*-
#########################################################################
# File Name: common/VideoClip.py
# Author: Toka
# mail: fengweitao@sensetime.com
# Created Time: 2018年07月27日 星期五 14时34分28秒
#########################################################################
from senseTk.functions import autoPattern
import math
import os
import cv2
from cv2 import VideoWriter
from cv2 import VideoCapture


class FakeCV2(object):

    def __init__(self, cvx):
        self.CV_CAP_PROP_FPS = cvx.CAP_PROP_FPS
        self.CV_CAP_PROP_FRAME_COUNT = cvx.CAP_PROP_FRAME_COUNT
        self.CV_CAP_PROP_POS_FRAMES = cvx.CAP_PROP_POS_FRAMES
        self.CV_CAP_PROP_FRAME_WIDTH = cvx.CAP_PROP_FRAME_WIDTH
        self.CV_CAP_PROP_FRAME_HEIGHT = cvx.CAP_PROP_FRAME_HEIGHT
        self.CV_CAP_PROP_POS_AVI_RATIO = cvx.CAP_PROP_POS_AVI_RATIO
        self.CV_FOURCC = cvx.VideoWriter_fourcc


try:
    cv2.cv
except AttributeError as e:
    cv2.cv = FakeCV2(cv2)


class ImgVideoCapture(object):

    DEFAULT_FMT = '%06d.jpg'

    def __init__(self, img_dir=None, fmt=DEFAULT_FMT, start=1):
        if img_dir is not None:
            if not self.open(img_dir, fmt, start):
                raise Exception('Unable to load image.')

    def open(self, img_dir, fmt=DEFAULT_FMT, start=1):
        self.i_root = img_dir
        self.fmt = fmt
        self.start = start
        # print 'testing',self.i_root+'/'+'%05d.png'%1
        im = cv2.imread(img_dir+'/'+fmt % start)
        if im is None:
            return False
        self.W = im.shape[1]
        self.H = im.shape[0]
        self.ptr = 0
        self.cnt = 0
        while 1:
            if not os.path.isfile(img_dir+'/'+fmt % (start+self.cnt)):
                break
            self.cnt += 1
        return True

    def isOpened(self):
        return self.i_root is not None and os.path.isdir(self.i_root)

    def get(self, code):
        if code == cv2.cv.CV_CAP_PROP_FPS:
            return 25
        if code == cv2.cv.CV_CAP_PROP_FRAME_COUNT:
            return self.cnt
        if code == cv2.cv.CV_CAP_PROP_POS_FRAMES:
            return self.ptr
        if code == cv2.cv.CV_CAP_PROP_FRAME_WIDTH:
            return self.W
        if code == cv2.cv.CV_CAP_PROP_FRAME_HEIGHT:
            return self.H

    def set(self, code, value):
        if code == cv2.cv.CV_CAP_PROP_POS_FRAMES:
            self.ptr = value

    def read(self):
        if self.ptr >= self.cnt:
            return False, None
        im = cv2.imread(self.i_root+'/'+self.fmt % (self.start+self.ptr))
        self.ptr += 1
        flag = True
        if im is None:
            flag = False
        return flag, im

    def release(self):
        pass


class VideoClipReader(object):

    def __init__(self, path, fmt=None, start=1):
        if os.path.isdir(path):
            if fmt is None:
                try:
                    tryfmt = autoPattern(path)
                    if tryfmt is None:
                        fmt = ImgVideoCapture.DEFAULT_FMT
                    else:
                        fmt = tryfmt
                except Exception as e:
                    fmt = ImgVideoCapture.DEFAULT_FMT
            self.backend = ImgVideoCapture(path, fmt, start)
        else:
            self.backend = VideoCapture(path)

    def read(self):
        return self.backend.read()

    def isOpened(self):
        return self.backend.isOpened()

    def release(self):
        return self.backend.release()

    def get(self, code):
        return self.backend.get(code)

    def set(self, code, value):
        return self.backend.set(code, value)

    def ImgSize(self):
        return int(self.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)), int(self.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT))

    def fps(self):
        fps = self.get(cv2.cv.CV_CAP_PROP_FPS)
        if math.isnan(fps):
            fps = 1./self.get(cv2.cv.CV_CAP_PROP_POS_AVI_RATIO)
        return fps

    def length(self):
        return int(self.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT))

    def __setattr__(self, x, y):
        if x == 'pos':
            self.set(cv2.cv.CV_CAP_PROP_POS_FRAMES, y)
        else:
            super(VideoClipReader, self).__setattr__(x, y)

    def __getattribute__(self, x):
        if x == 'pos':
            return self.get(cv2.cv.CV_CAP_PROP_POS_FRAMES)
        else:
            return super(VideoClipReader, self).__getattribute__(x)

    def __len__(self):
        return int(self.length())

    def __getitem__(self, ind):
        if ind != int(self.get(cv2.cv.CV_CAP_PROP_POS_FRAMES)):
            self.set(cv2.cv.CV_CAP_PROP_POS_FRAMES, ind)
        s, im = self.read()
        if not s or im is None:
            raise Exception('read img error')
        return im


class ImgVideoWriter(object):

    def __init__(self, path, fmt=ImgVideoCapture.DEFAULT_FMT, start=1):
        self.path = path
        self.fmt = fmt
        self.start = start
        self.ptr = 0
        if not os.path.exists(path):
            os.mkdir(path)
        assert os.path.isdir(path)

    def write(self, im):
        ret = cv2.imwrite(self.path+'/'+self.fmt % (self.start + self.ptr), im)
        self.ptr += 1
        return ret

    def release(self):
        pass


class VideoClipWriter(object):

    NORMAL_VIDEO = 1
    IMG_VIDEO = 2

    def __init__(self, path, video_type, fps=25.0, size=None, fmt=ImgVideoCapture.DEFAULT_FMT, start=1):
        self.typ = video_type
        if video_type == VideoClipWriter.IMG_VIDEO:
            self.backend = ImgVideoWriter(path, fmt, start)
        else:
            if size is not None:
                self.backend = VideoWriter(
                    path, cv2.cv.CV_FOURCC('D', 'I', 'V', 'X'), fps, size)
            else:
                raise Exception('video size is needed.')

    def write(self, im):
        return self.backend.write(im)

    def release(self):
        return self.backend.release()
