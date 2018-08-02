#!/usr/bin/python
# -*- coding: utf8 -*-
#########################################################################
# File Name: common/Det.py
# Author: Toka
# mail: fengweitao@sensetime.com
# Created Time: 2018年07月27日 星期五 13时39分48秒
#########################################################################
import copy

class Det(object):

    x1 = 0 
    y1 = 0 
    w = 5 
    h = 5 
    __free__ = False

    OBJECT_PED = 1
    OBJECT_OTHER = 2
    OBJECT_VEHICLE = 3

    def __init__(self, x1, y1, w, h, cls = None, confidence = 1.,
     uid = -1, fr = -1, status = -1):
        self.x1 = x1
        self.y1 = y1
        self.w = w 
        self.h = h 
        self.label = cls 
        self.conf = confidence
        self.uid = uid
        self.fr = fr
        self.status = status
        
    def __setattr__(self, x, y): 
        if not self.__free__ and (x=='x2' or x=='y2' or x=='cx' or x=='cy'):
            raise Exception('cannot modify infered properties')
        super(Det, self).__setattr__(x, y)
        if x=='x1' or x=='y1' or x=='w' or x=='h':
            self.__free__ = True
            self.x2 = self.x1 + self.w
            self.y2 = self.y1 + self.h
            self.cx = (self.x1 + self.x2)/2
            self.cy = (self.y1 + self.y2)/2
            self.__free__ = False
        
    def area(self):
        w = max(self.w, 0)
        h = max(self.h, 0)
        return w*h
    
    def intersection(self, o):
        mx1 = max(self.x1, o.x1)
        my1 = max(self.y1, o.y1)
        mx2 = min(self.x2, o.x2)
        my2 = min(self.y2, o.y2)
        ix = (mx2 - mx1) if (mx2 - mx1 > 0) else 0
        iy = (my2 - my1) if (my2 - my1 > 0) else 0
        return ix*iy

    def union(self, o):
        return self.area() + o.area() - self.intersection(o)

    def iou(self, o):
        intersect = self.intersection(o)
        return intersect / (self.area() + o.area() - intersect);

    def lt(self, ox = 0, oy = 0):
        return (self.x1 + ox, self.y1 + oy)

    def rb(self, ox = 0, oy = 0):
        return (self.x1 + self.w + ox, self.y1 + self.h + oy)

    def _trim(self, sz = None):
        if sz is not None:
            w, h = sz
            self.x1 = max(self.x1, 0)
            self.y1 = max(self.y1, 0)
            self.w = min(self.w, w-self.x1)
            self.h = min(self.h, h-self.y1)
        self.x1, self.y1, self.w, self.h = map(int, self.toList())
        return self

    def trim(self, sz = None):
        ret = copy.copy(self)
        return ret._trim(sz)

    def _astype(self, dtype):
        self.x1, self.y1, self.w, self.h = map(dtype, self.toList())
        return self

    def astype(self, dtype):
        ret = copy.copy(self)
        return ret._astype(dtype)

    def __mul__(self, a):
        if isinstance(y, float) or isinstance(y, int):
            nw = self.w*a
            nh = self.h*a
            cx = self.cx
            cy = self.cy
            self.x1 = cx - nw/2
            self.y1 = cy - nh/2
            self.w = nw
            self.h = nh

    def __str__(self):
        return '%d,%d,%.2f,%.2f,%.2f,%.2f,%.3f,%s,%d,-1'%\
            (self.fr, self.uid, self.x1, self.y1, self.w, self.h,
             self.conf, str(self.label), self.status)

    def toList(self):
        return [self.x1, self.y1, self.w, self.h]

    def toTuple(self):
        return (self.x1, self.y1, self.w, self.h)


class VidDet(object): #general Det of Video

    min_fr = 1000000000
    max_fr = -1

    @staticmethod
    def readline(row):
        bk = row
        row = row.strip().split(',')
        if len(row)>10 or len(row)<9:
            return VidDet.readline2(bk)
        fr = int(row[0])
        uid = int(row[1])
        x1 = float(row[2])
        y1 = float(row[3])
        w = float(row[4])
        h = float(row[5])
        enable = int(row[6])
        cl = int(row[7])
        conf = float(row[8])
        res = Det(x1,y1,w,h,
            cls = cl, confidence = conf,
            fr = fr, uid = uid, status = enable)
        return res

    @staticmethod
    def readline2(row):
        bk = row
        row = row.strip().split(' ')
        fr = int(row[0])
        uid = int(row[1])
        x1 = int(row[2])
        y1 = int(row[3])
        w = int(row[4])
        h = int(row[5])
        cl = int(row[7])
        conf = float(row[6])
        res = Det(x1,y1,w,h,cls = cl,confidence = conf,
            fr = fr, uid = uid)
        return res

    def toJson(self, frfirst = False):
        js = {}
        if frfirst:
            for i in self.frameRange():
                tmp = {}
                js['%06d'%i] = tmp
                one = self[i]
                for it in one:
                    tmp['%02d'%it.uid] = [it.x1, it.y1, it.x2, it.y2]
            
        else:
            for one in self.allPed():
                tmp = {}
                js['%02d'%one] = tmp
                one = self(one)
                for i in one.frameRange():
                    it = one[i][0]
                    tmp['%06d'%i] = [it.x1, it.y1, it.x2, it.y2]
        return js


    def __init__(self, fn = None, dealer = None, filter = None):
        self.frd = {}
        self.ped = {}
        self.cache = {}
        if fn is not None:
            f = open(fn)
            rows = f.readlines()
            for row in rows:
                if dealer is None:
                    D = self.readline(row)
                else:
                    D = dealer(row)
                if D is None or filter is not None and not filter(D): continue
                # print type(D)
                if isinstance(D, Det)==False:
                    # print D
                    fr, uid, x1, y1, w, h, label, conf = D
                    D = Det(x1,y1,w,h,cls = label, confidence = conf,
                        fr = fr, uid = uid)
                self.append_data(D)
            f.close()

    def __getitem__(self, index):
        if isinstance(index, int):
            if index in self.frd:
                return self.frd[index]
            else:
                return []
        if isinstance(index, slice):
            res = self.__class__()
            for i in xrange(*(index.indices(self.max_fr+1))):
                if i in self.frd:
                    for one in self.frd[i]:
                        res.append_data(copy.copy(one))
            return res
        raise Exception('index must be integer or slice. NOT  %s'%str(index))

    def __setitem__(self, index, val):
        if isinstance(index, int):
            if val is None:
                self.frd[index] = []
                return
            if isinstance(val, list):
                self.frd[index] = val
            else:
                self.frd[index] = [val]
            self.max_fr = max(self.max_fr, index)
            self.min_fr = min(self.min_fr, index)
        elif isinstance(index, slice):
            if val is None:
                for i in xrange(*(index.indices(self.max_fr+1))):
                    self.frd[i] = []
                return
            if isinstance(val, list):
                cnt = 0
                for i in xrange(*(index.indices(self.max_fr+1))):
                    cnt+=1
                if len(val)==cnt:
                    cnt = 0
                    for i in xrange(*(index.indices(self.max_fr+1))):
                        self.frd[i] = val[cnt]
                        cnt += 1
                        self.max_fr = max(self.max_fr, i)
                        self.min_fr = min(self.min_fr, i)
                elif index.stop is None:
                    self.__setitem__(index, None)
                    i = index.start
                    j = 0
                    n = len(val)
                    while j<n:
                        self.frd[i] = val[j]
                        j+=1
                        if index.step is None:
                            i+=1
                        else:
                            i+=index.step
                        self.max_fr = max(self.max_fr, i)
                        self.min_fr = min(self.min_fr, i)
                else:
                    raise Exception('cannot place %d elements in %d length'%(len(val), cnt))
            elif isinstance(val, self.__class__):
                if index.stop is None:
                    self.__setitem__(index, None)
                    mxf = max(self.max_fr, val.max_fr)
                    for i in xrange(*(index.indices(mxf+1))):
                        self.frd[i] = val[i]
                        self.max_fr = max(self.max_fr, i)
                        self.min_fr = min(self.min_fr, i)
                else:
                    for i in xrange(*(index.indices(self.max_fr+1))):
                        self.frd[i] = val[i]
        else:
            raise Exception('index must be integer or slice. NOT  %s'%str(index))

    def frameRange(self):
        return range(self.min_fr, self.max_fr+1)

    def allPed(self):
        return self.ped.keys()

    def allFr(self):
        return self.frd.keys()

    def append_data(self, D):
        if D.uid not in self.ped:
            self.ped[D.uid] = []
        self.ped[D.uid].append(D)
        if D.fr not in self.frd:
            self.frd[D.fr] = []
        self.frd[D.fr].append(D)
        self.min_fr = min(self.min_fr, D.fr)
        self.max_fr = max(self.max_fr, D.fr)

    def __call__(self, ind):
        if ind in self.cache:
            return self.cache
        if ind in self.ped:
            ret = self.__class__()
            for one in self.ped[ind]:
                ret.append_data(one)
            self.cache[ind] = ret
            return ret
        else:
            return None
