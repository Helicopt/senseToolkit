#!/usr/bin/python
# -*- coding: utf8 -*-
#########################################################################
# File Name: functions/__init__.py
# Author: Toka
# mail: fengweitao@sensetime.com
# Created Time: 2018年07月27日 星期五 15时32分36秒
#########################################################################
from __future__ import print_function
import cv2
import re
import os
import time
import inspect
import pickle
import os.path as osp
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

def autoPattern(path, loose_fmt = True):
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
            fns = list(filter(lambda x: not re.match('^\.', x), os.listdir(path)))
        else:
            fns = [path]
    else:
        fns = [i for i in path]
    if True:
        rec = {}
        fmt = []
        pre = ''
        for i in fns:
            r, e = guess(i)
            rec[r] = rec.get(r, 0) + 1
            fmt.append([r, e])
            if loose_fmt == False and pre!='' and len(e)!=len(pre):
                return None
            pre = e
        if loose_fmt:
            n = len(fns)
            k = None
            for i in rec:
                if rec[i]>(n>>1):
                    k = i
                    break
            if k is None:
                return None
            else:
                fmt = list(filter(lambda x: x[0]==k, fmt))
                pre = fmt[0][1]
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
    if n <= 0 or m <=0:
        return [], [i for i in range(n)], [i for i in range(m)]
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

def brief_pos_bar(percentage=0):
    if percentage > 0.99999:
        print('100 % DONE!')
    else:
        print('%.2f %%'%(percentage * 100), end='\r')

global sfp_cnt
sfp_cnt = 0

def inspect_data(x, tag=None, tmp_path=None, global_cnt=-1, silent=True, on_exit=True):
    if tag is None:
        tag = inspect.getouterframes(inspect.currentframe())[-1].filename
    if tmp_path is None:
        path='/tmp/save_for_comparision.sfp'
    else:
        path = tmp_path
    global sfp_cnt
    sfp_cnt += 1
    if global_cnt > 0 and sfp_cnt < global_cnt:
        return
    try:
        import torch
        has_torch = True
    except:
        has_torch = False
    try:
        import mxnet
        has_mxnet = True
    except:
        has_mxnet = False
    def deal(a):
        if isinstance(a, set):
            return a
        if isinstance(a, (list, tuple)):
            return [deal(i) for i in a]
        if isinstance(a, (int, float, str, bytes)):
            return a
        if isinstance(a, dict):
            return {i: deal(j) for i, j in a.items()}
        if isinstance(a, np.ndarray):
            return [deal(i) for i in a]
        if has_torch and isinstance(a, torch.Tensor):
            if not silent: print(a.shape)
            return deal(a.detach().cpu().numpy())
        if has_mxnet and isinstance(a, mxnet.ndarray.NDArray):
            if not silent: print(a.shape)
            return deal(a.asnumpy())
        if isinstance(a, np.integer):
            return int(a)
        if isinstance(a, np.floating):
            return float(a)
        if isinstance(a, senseTk.common.Det):
            return a.toList()
        raise NotImplementedError('Unknown type %s'%type(a))
    if not osp.exists(path):
        d = {}
    else:
        try:
            with open(path, 'rb') as fd:
                d = pickle.load(fd)
        except:
            d = {}
    d[tag] = deal(x)
    with open(path, 'wb') as fd:
        pickle.dump(d, fd, protocol=2)
    if not silent: print()
    if on_exit: exit(0)

def compare(d1, d2, k1, k2, eps=1e-6, max_mistakes=10, miscnt=0):
    kwargs = {'eps': eps, 'max_mistakes': max_mistakes, 'miscnt': miscnt}
    def assertType(d1, d2, k1, k2):
        if type(d1)!=type(d2):
            print('typediff: %s (%s) vs %s (%s)'%(k1, type(d1), k2, type(d2)))
            return False
        return True
    def assertLen(d1, d2, k1, k2):
        if len(d1)!=len(d2):
            print('lendiff: %s (%s) vs %s (%s)'%(k1, len(d1), k2, len(d2)))
            return False
        return True
    def assertKey(d1, d2, k1, k2):
        if len(set(d1.keys()) - set(d2.keys()))!=0 or len(set(d2.keys()) - set(d1.keys()))!=0:
            print('keydiff: %s (%s) vs %s (%s)'%(k1, set(d1.keys()) - set(d2.keys()), k2, set(d2.keys()) - set(d1.keys()) ))
            return False
        return True
    def assertValue(d1, d2, k1, k2):
        nonlocal miscnt
        if d1!=d2:
            print('valdiff: %s (%s) vs %s (%s)'%(k1, d1, k2, d2))
            miscnt += 1
            if miscnt > max_mistakes:
                return False
        return True
    def assertClose(d1, d2, k1, k2):
        nonlocal miscnt
        if abs(d1 - d2) > eps and abs(d1 - d2) / max(min(abs(d1), abs(d2)), eps) > eps: 
            print('valdiff: %s (%s) vs %s (%s)'%(k1, d1, k2, d2))
            miscnt += 1
            if miscnt > max_mistakes:
                return False
        return True
    def assertSet(d1, d2, k1, k2):
        if len(d1 & d2) != len(d1) or len(d1) != len(d2):
            print('set diff: (%d in common)' % len(d1 & d2))
            print('    %s only (%d): '%(k1, len(d1 - d2)))
            print('        %s'%(d1 - d2))
            print('    %s only (%d): '%(k2, len(d2 - d1)))
            print('        %s'%(d2 - d1))
            return False
        return True
    if not assertType(d1, d2, k1, k2):
        return False, miscnt + 1
    found = False
    if isinstance(d1, (list, tuple)):
        found = True
        if not assertLen(d1, d2, k1, k2): return False, miscnt + 1
        for k, (i, j) in enumerate(zip(d1, d2)):
            f, c = compare(i, j, k1+'[%d]'%k, k2+'[%d]'%k, **kwargs)
            kwargs['miscnt'] = c
            miscnt = c
            if not f: return False, kwargs['miscnt']
    if isinstance(d1, dict):
        found = True
        if not assertKey(d1, d2, k1, k2): return False, miscnt + 1
        for k in d1.keys():
            f, c = compare(d1[k], d2[k], k1+'.%s'%str(k), k2+'.%s'%str(k), **kwargs)
            kwargs['miscnt'] = c
            miscnt = c
            if not f: return False, kwargs['miscnt']
    if isinstance(d1, (int, str, bytes)):
        found = True
        if not assertValue(d1, d2, k1, k2): return False, miscnt
    if isinstance(d1, float):
        found = True
        if not assertClose(d1, d2, k1, k2): return False, miscnt
    if isinstance(d1, set):
        found = True
        if not assertSet(d1, d2, k1, k2): return False, miscnt + 1
    assert found, 'Unknown Type %s'%type(d1)
    return True, miscnt

def dislpay_diff(path=None, eps=1e-7, max_value_diff=0):
    if path is None:
        path='/tmp/save_for_comparision.sfp'
    with open(path, 'rb') as fd:
        d = pickle.load(fd)
    keys = list(d.keys())
    for i, k1 in enumerate(keys):
        print('***', k1, type(d[k1]), '***')
        for j, k2 in enumerate(keys):
            if i>=j: continue
            print('--'*20)
            f, c = compare(d[k1], d[k2], k1, k2, eps=eps, max_mistakes=max_value_diff)
            print('--'*20)
            if f:
                print('%s is same as %s (eps %a, mistake %d)'%(k1, k2, eps, c))
            else:
                print('%s differs from %s (eps %a, mistake %d)'%(k1, k2, eps, c))
