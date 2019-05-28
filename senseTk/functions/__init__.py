#!/usr/bin/python
# -*- coding: utf8 -*-
#########################################################################
# File Name: functions/__init__.py
# Author: Toka
# mail: fengweitao@sensetime.com
# Created Time: 2018年07月27日 星期五 15时32分36秒
#########################################################################

import cv2
import re
import os
import time
from ..extension import flow

def streamForward(source, destination):
	while True:
		s, im = source.read()
		if not s or im is None: break
		destination.write(im)

def drawOnImg(im, D, color = (255,0,0), bold = 0.5, stamp = False, conf = False):
	D = D.trim()
	cv2.rectangle(im, D.lt(), D.rb(), color, int(bold*2))
	offset = 16
	cv2.putText(im, '%d'%D.uid, D.lt(2, offset), cv2.FONT_HERSHEY_DUPLEX, bold, color)
	offset+=int(32*bold)
	if stamp:
		cv2.putText(im, '%d'%D.fr, D.lt(2, offset), cv2.FONT_HERSHEY_DUPLEX, bold, color)
		offset+=int(32*bold)
	if conf:
		cv2.putText(im, '%.2f'%D.conf, D.lt(2, offset), cv2.FONT_HERSHEY_DUPLEX, bold, color)
		offset+=int(32*bold)

def detCrop(im, d):
	h, w = im.shape[:2]
	d = d.trim((w, h))
	if d.area()>1: return im[d.y1:d.y2, d.x1:d.x2]
	return None

def drawText(im, pos, s, bold = 0.5, color = (255,0,0), fm = cv2.FONT_HERSHEY_DUPLEX):
	cv2.putText(im, s, pos, fm, bold, color)

def alignTrackSet2Video(clip, track, start = 1, drawer = drawOnImg, action = None, dealer = None):
	while True:
		s, im = clip.read()
		if not s or im is None: break
		if dealer is not None:
			dealer(im, track[start])
		else:
			for one in track[start]:
				drawer(im, one)
		action(im)
		start+=1

def cvWait():
    while True:
        ret = cv2.waitKey(0)
        if (ret&0xFF)==ord('q'):
            exit(42)
        if (ret&0xFF)==ord('n'):
            break

def cvShow(im, label = 'test'):
	cv2.imshow(label, im)
	cvWait()

def autoPattern(path):
    def guess(s):
        d = ''
        r = ''
        e = []
        for i in s:
            if '0'<=i<='9':
                d+=i
            else:
                if d!='':
                    if d[0]=='0' and len(d)!=1:
                        e.append('%%0%dd'%(len(d)))
                    else:
                        e.append('%d')
                    r+='#d'
                    d = ''
                if i=='#':
                    r+='##'
                else:
                    r+=i
        if d!='':
            if d[0]=='0' and len(d)!=1:
                e.append('%%0%dd'%(len(d)))
            else:
                e.append('%d')
            r+='#d'
        return r, e
    if isinstance(path, str):
        if os.path.isfile(path):
            return path
        elif os.path.isdir(path):
            fns = filter(lambda x: not re.match('^\.', x), os.listdir(path))
    else:
        fns = [i for i in path]
    if True:
        fmt = []
        pre = ''
        for i in fns:
            r, e = guess(i)
            fmt.append([r, e])
            if pre!='' and len(e)!=len(pre):
                return None
            pre = e
        for i in range(len(pre)):
            tag = ''
            for j in range(len(fmt)):
                if fmt[j][1][i]!='%d':
                    if tag=='':
                        tag = fmt[j][1][i]
                    elif fmt[j][1][i]!=tag:
                        return None
            if tag!='':
                for j in range(len(fmt)):
                    fmt[j][1][i] = tag
        def mapping(s, t):
            r = ''
            n = len(s)
            i = 0
            j = 0
            while i < n:
                if s[i]=='#':
                    if i+1<n:
                        if s[i+1]=='d' or s[i+1]=='s':
                            r+=t[j]
                            j+=1
                        else:
                            r+=s[i+1]
                        i+=1
                    else:
                        r+='#'
                else:
                    r+=s[i]
                i+=1
            return r
        pre = ''
        for i in range(len(fmt)):
            fmt[i] = mapping(*fmt[i])
            if pre!='' and fmt[i]!=pre:
                return None
            pre = fmt[i]
        return pre

def LAP_Matching(Lis, Ris, CostFunc, Lapsolver = 'flow'):
    '''
    Lis, Ris: two list of items, representing Left side
              and the Right side nodes of the Bipartie-Graph
    CostFunc: cost function to create a weighted edge (of 2 nodes),
              return a float in range (0,1] representing the
              weight and return None or 0 representing no such edge
    Lapsolver: Currently support flow module only
    '''
    n = len(Lis)
    m = len(Ris)
    uid = int(time.time() * 10000 % int(1e9+7))
    maxn = int(2e6)
    thr = maxn - 1
    alpha = 1e6
    flow.createFlow(uid)
    flow.clear(uid)
    flow.setThr(uid, thr)
    flow.setNodes(uid, n, m)
    for i, li in enumerate(Lis):
        for j, ri in enumerate(Ris):
            cost = CostFunc(li, ri)
            if cost is not None and cost>0:
                c = float(cost) * alpha
                c = maxn - int(c)
                if c >= thr: continue
                flow.addEdge(uid, i+1, n+j+1, c)
    match = flow.flow(uid)
    matched = []
    lmiss = []
    rmiss = set([i for i in range(m)])
    for i in range(n):
        ind = match[i + 1] - n - 1
        if ind>=0:
            matched.append((i, ind))
            rmiss.remove(ind)
        else:
            lmiss.append(i)
    flow.release(uid)
    return matched, lmiss, list(rmiss)

