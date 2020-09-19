#!/usr/bin/python
# -*- coding: utf8 -*-
#########################################################################
# File Name: ../scripts/visualize.py
# Author: Toka
# mail: fengweitao@sensetime.com
# Created Time: 2018年07月27日 星期五 17时15分04秒
#########################################################################
import senseTk
from senseTk.common import *
from senseTk.functions import *
from senseTk.magic import *

if __name__ == '__main__':
    # __author__ == '__toka__'
    print senseTk.__version__
    # vid = VideoClipReader('/home/sensetime/data/MOT16video/MOT16-05.avi')
    # wri = VideoClipWriter('/home/sensetime/data/MOT16video/testst.avi', video_type = VideoClipWriter.NORMAL_VIDEO, fps = vid.fps(), size = tuple(map(int, vid.ImgSize())))
    # streamForward(vid, wri)
    # vid = VideoClipReader('/home/sensetime/toka/MOT/train/MOT16-04/img1')
    # vid = VideoClipReader('/home/sensetime/data/MOT16video/MOT16-05.avi')
    # print vid.fps(), vid.length(), vid.ImgSize()
    # dt = TrackSet('/home/sensetime/toka/MOT/train/MOT16-05/gt/gt.txt')
    # alignTrackSet2Video(vid, dt, action = cvShow)
    # vis
    # data = ['ftp://10.10.15.115/lustre/fengweitao/Siamese_FC/train5/samples/000001.02.crop.z_000427.31.crop.x_-1_%s.jpg'%i for i in ['A', 'B']]
    # data = ['http://10.1.30.165:8000/%06d.jpg'%i for i in xrange(1,100)]
    # data = ['ftp://10.1.30.165:2121/img1/%06d.jpg'%i for i in xrange(1,100)]
    # data = [getFile('ftp://10.1.30.165:2121/img1/%06d.jpg'%i) for i in xrange(1,100)]
    data = VideoClipReader('/home/sensetime/data/MOT16video/MOT16-05.avi')

    def cb(im, ind, **kwargs):
        import cv2
        cv2.rectangle(im, (50, 50), (60, 60+ind), (0, 0, 0), 1)
        if kwargs['type'] == 'refresh':
            kwargs['info'].setText('%03d' % ind)
    requireQA()
    _ = IMGallery(data).show(cb)
