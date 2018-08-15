#!/usr/bin/python
# -*- coding: utf8 -*-
#########################################################################
# File Name: VI.py
# Author: Toka
# mail: fengweitao@sensetime.com
# Created Time: 2018年08月15日 星期三 21时56分08秒
#########################################################################
from senseTk.common import *
from senseTk.functions import *
import argparse

if __name__=='__main__':
    # __author__ == '__toka__'
    parser = argparse.ArgumentParser(description = 'Tool for Video-Imageset exchange.')
    parser.add_argument('source', help = 'source video/imgset')
    parser.add_argument('destination', help = 'target video/imgset')
    parser.add_argument('-t', '--type', default='auto', type=str, choices=['auto', 'img', 'video'], help = 'target type, auto is to change to different from source')
    parser.add_argument('-i', '--inverse', action = 'store_true', help = 'switch src and dest')
    parser.add_argument('--ifmt', default='', type=str, help = 'decide input imgset format')
    parser.add_argument('--istart', default=1, type=int, help = 'input imgset start offset')
    parser.add_argument('--ofmt', default='', type=str, help = 'decide output imgset format')
    parser.add_argument('--ostart', default=1, type=int, help = 'output imgset start offset')
    args = parser.parse_args()
    if args.inverse:
        src = args.destination
        dst = args.source
    else:
        src = args.source
        dst = args.destination
    if args.ifmt=='':
        a = VideoClipReader(src, start = args.istart)
    else:
        a = VideoClipReader(src, fmt = args.ifmt, start = args.istart)
    if isinstance(a.backend, ImgVideoCapture):
        typ = VideoClipWriter.NORMAL_VIDEO
    else:
        typ = VideoClipWriter.IMG_VIDEO
    if args.type=='img':
        typ = VideoClipWriter.IMG_VIDEO
    if args.type=='video':
        typ = VideoClipWriter.NORMAL_VIDEO
    if args.ofmt=='':
        b = VideoClipWriter(dst, typ, size=a.ImgSize(), start = args.ostart)
    else:
        b = VideoClipWriter(dst, typ, size=a.ImgSize(), fmt = args.ofmt, start = args.ostart)
    streamForward(a, b)
    a.release()
    b.release()
