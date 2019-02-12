#!/usr/bin/python
# -*- coding: utf8 -*-
#########################################################################
# File Name: transfer.py
# Author: Toka
# mail: fengweitao@sensetime.com
# Created Time: 2019年02月12日 星期二 21时14分20秒
#########################################################################
import senseTk
from senseTk.common import *
import argparse

if __name__=='__main__':
    # __author__ == '__toka__'
    parser = argparse.ArgumentParser()
    parser.add_argument('src', type=str, help='source file')
    parser.add_argument('src_format', type=str, help='source format')
    parser.add_argument('dst', type=str, help='destination file')
    parser.add_argument('dst_format', type=str, help='destination format')
    args = parser.parse_args()
    a = TrackSet(args.src, formatter=args.src_format)
    with open(args.dst, 'w') as fd:
        a.dump(fd, formatter=args.dst_format)
