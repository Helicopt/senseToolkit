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
from senseTk.functions import *
import argparse

if __name__=='__main__':
    # __author__ == '__toka__'
    parser = argparse.ArgumentParser(description = 'Tool for Visualization.')
    parser.add_argument('src', help = 'source video/imgset')
    parser.add_argument('--ifmt', default='', type=str, help = 'decide input imgset format')
    parser.add_argument('--istart', default=1, type=int, help = 'input imgset start offset')
    parser.add_argument('--trackset', default='', type=str, help = 'file recording tracklets')
    parser.add_argument('--format', '-f', default='MOT', type=str, choices = ['MOT', 'MOTwithScore', 'Label', 'Detect'], help = 'trackset format')
    parser.add_argument('--filter', '-F', default=0., type=float, help = 'filtering confidence (only show larger than threshold)')
    args = parser.parse_args()
    if args.ifmt=='':
        a = VideoClipReader(args.src, start = args.istart)
    else:
        a = VideoClipReader(args.src, fmt = args.ifmt, start = args.istart)
    requireQA()
    if args.trackset!='':
        ffunc = lambda x: x.conf > args.filter
        if args.format=='MOTwithScore':
            g = TrackSet(args.trackset, formatter = 'fr.i id.i x1 y1 w h cf st la.s -1', filter = ffunc)
        elif args.format=='Detect':
            g = TrackSet(args.trackset, formatter = 'fr.i id.i x1 y1 w h cf la.s -1 -1', filter = ffunc)
        elif args.format=='Label':
            g = TrackSet(args.trackset, formatter = 'fr.i id.i x1 y1 w h cf la.s', filter = ffunc)
        else:
            g = TrackSet(args.trackset, filter = ffunc)
        def cb(im, ind, **kwargs):
            if kwargs['type']==IMGallery.E_REFRESH:
                txt = ''
                for dt in g[ind+g.min_fr]:
                    drawOnImg(im, dt, conf = (args.format!='MOT'))
                    txt+='%d %d] %d %d %d %d %.3f (%d) {%s}\n'%(dt.fr, dt.uid, dt.x1, dt.y1, dt.w, dt.h, dt.conf, dt.status, dt.label)
                kwargs['info'].setText(txt)
        t = IMGallery(a).show(cb)
    else:
        t = IMGallery(a).show()

