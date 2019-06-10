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

if __name__ == '__main__':
    # __author__ == '__toka__'
    parser = argparse.ArgumentParser(
        'python -m senseTk.apps.visualize', description='Tool for Visualization.')
    parser.add_argument('src', help='source video/imgset')
    parser.add_argument('--ifmt', default='', type=str,
                        help='decide input imgset format')
    parser.add_argument('--istart', default=1, type=int,
                        help='input imgset start offset')
    parser.add_argument('--trackset', default='', type=str,
                        help='file recording tracklets')
    parser.add_argument('--format', '-f', default='MOT', type=str,
                        choices=['MOT', 'MOTwithScore', 'Label', 'Detect'], help='trackset format')
    parser.add_argument('--filter', '-F', default=-2., type=float,
                        help='filtering confidence (only show larger than threshold)')
    parser.add_argument('--diff', '-d', default=None, type=str,
                        help='another file containing tracklets for comparison')
    args = parser.parse_args()
    if args.ifmt == '':
        a = VideoClipReader(args.src, start=args.istart)
    else:
        a = VideoClipReader(args.src, fmt=args.ifmt, start=args.istart)
    requireQA()
    if args.trackset != '':
        di = None

        def ffunc(x): return x.conf > args.filter
        if args.format == 'MOTwithScore':
            g = TrackSet(
                args.trackset, formatter='fr.i id.i x1 y1 w h cf st.i la.s -1', filter=ffunc)
            if args.diff is not None:
                di = TrackSet(
                    args.diff, formatter='fr.i id.i x1 y1 w h cf st.i la.s -1', filter=ffunc)
        elif args.format == 'Detect':
            g = TrackSet(
                args.trackset, formatter='fr.i id.i x1 y1 w h cf la.s -1 -1', filter=ffunc)
            if args.diff is not None:
                di = TrackSet(
                    args.diff, formatter='fr.i id.i x1 y1 w h cf la.s -1 -1', filter=ffunc)
        elif args.format == 'Label':
            g = TrackSet(
                args.trackset, formatter='fr.i id.i x1 y1 w h cf la.s', filter=ffunc)
            if args.diff is not None:
                di = TrackSet(
                    args.diff, formatter='fr.i id.i x1 y1 w h cf la.s', filter=ffunc)
        else:
            g = TrackSet(args.trackset, filter=ffunc)
            if args.diff is not None:
                di = TrackSet(args.diff, filter=ffunc)
        global mysel, idmapping, invmapping
        mysel = None
        idmapping = {}
        invmapping = {}

        def cb(im, ind, **kwargs):
            global mysel, idmapping, invmapping
            if kwargs['type'] == IMGallery.E_REFRESH:
                txt = ''
                idmapping = {}
                invmapping = {}
                mydet = None
                if di is not None:
                    matched, lmiss, rmiss = LAP_Matching(g[ind + 1], di[ind + 1],
                                                         lambda x, y: x.iou(y) if x.iou(y) > 0.5 else None)
                    matched = {i[0]: True for i in matched}
                    lmiss = {i: True for i in lmiss}
                    rmiss = [di[ind + 1][i] for i in rmiss]
                    for dt in rmiss:
                        drawOnImg(im, dt, conf=(args.format != 'MOT'),
                                  color=(150, 150, 150))
                for i, dt in enumerate(g[ind+1]):
                    if dt.uid == mysel:
                        mydet = dt
                    else:
                        if di is not None:
                            if i in matched:
                                drawOnImg(im, dt, conf=(
                                    args.format != 'MOT'), color=(0, 200, 0))
                            elif i in lmiss:
                                drawOnImg(im, dt, conf=(args.format != 'MOT'))
                        else:
                            drawOnImg(im, dt, conf=(args.format != 'MOT'))
                    txt += '%d %d] %d %d %d %d %.3f s(%d) #%s\n' % (
                        dt.fr, dt.uid, dt.x1, dt.y1, dt.w, dt.h, dt.conf, dt.status, dt.label)
                    idmapping[i] = dt.uid
                    invmapping[dt.uid] = i
                oldInfoPos = kwargs['info'].verticalScrollBar().value()
                oldSel = kwargs['info'].currentIndex()
                kwargs['info'].clear()
                kwargs['info'].addItems(txt[:-1].split('\n'))
                kwargs['info'].verticalScrollBar().setValue(oldInfoPos)
                kwargs['info'].setCurrentIndex(oldSel)
                if invmapping.get(mysel, None) is not None:
                    kwargs['info'].setCurrentRow(invmapping.get(mysel, None))
                if mydet is not None:
                    drawOnImg(im, mydet, conf=(args.format != 'MOT'),
                              color=(0, 200, 200), bold=0.7)
                kwargs['info'].setFocus()
            if kwargs['type'] == IMGallery.E_INFOCLICK:
                mysel = idmapping.get(kwargs['sel'], None)
                return mysel != None
            if kwargs['type'] == IMGallery.E_MPRESS:
                ox = kwargs['origin_x']
                oy = kwargs['origin_y']
                mi = -1
                for i, dt in enumerate(g[ind+1]):
                    if dt.x1+1 < ox < dt.x2+1 and dt.y1+1 < oy < dt.y2+1:
                        if mi < 0 or abs(ox-dt.cx)+abs(oy-dt.cy) < mi:
                            mi = abs(ox-dt.cx)+abs(oy-dt.cy)
                            mysel = dt.uid
                if mi != -1 and invmapping.get(mysel, None):
                    kwargs['info'].setCurrentRow(invmapping.get(mysel, None))
                    kwargs['info'].setFocus()
                return mi != -1

        t = IMGallery(a).show(cb)
    else:
        t = IMGallery(a).show()
