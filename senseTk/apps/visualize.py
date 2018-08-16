#!/usr/bin/python
# -*- coding: utf8 -*-
#########################################################################
# File Name: senseTk/apps/visualize.py
# Author: Toka
# mail: fengweitao@sensetime.com
# Created Time: 2018年08月16日 星期四 16时08分15秒
#########################################################################
from senseTk.common import *
from senseTk.magic import *
import argparse

if __name__=='__main__':
    # __author__ == '__toka__'
    parser = argparse.ArgumentParser(description = 'Tool for Visualization.')
    parser.add_argument('src', help = 'source video/imgset')
    parser.add_argument('--ifmt', default='', type=str, help = 'decide input imgset format')
    parser.add_argument('--istart', default=1, type=int, help = 'input imgset start offset')
    args = parser.parse_args()
    if args.ifmt=='':
        a = VideoClipReader(args.src, start = args.istart)
    else:
        a = VideoClipReader(args.src, fmt = args.ifmt, start = args.istart)
    requireQA()
    t = IMGallery(a).show()

