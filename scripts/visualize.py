#!/usr/bin/python
# -*- coding: utf8 -*-
#########################################################################
# File Name: ../scripts/visualize.py
# Author: Toka
# mail: fengweitao@sensetime.com
# Created Time: 2018年07月27日 星期五 17时15分04秒
#########################################################################

from senseTk.common import *
from senseTk.functions import *

if __name__=='__main__':
    # __author__ == '__toka__'
    # vid = VideoClipReader('/home/sensetime/toka/MOT/train/MOT16-04/img1')
    vid = VideoClipReader('/home/sensetime/data/MOT16video/MOT16-05.avi')
    print vid.fps(), vid.length(), vid.ImgSize()
    dt = TrackSet('/home/sensetime/toka/MOT/train/MOT16-05/gt/gt.txt')
    alignTrackSet2Video(vid, dt, action = cvShow)
