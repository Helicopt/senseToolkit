#!/usr/bin/python
# -*- coding: utf8 -*-
#########################################################################
# File Name: common/Det.py
# Author: Toka
# mail: fengweitao@sensetime.com
# Created Time: 2018年07月27日 星期五 13时39分48秒
#########################################################################
import copy
import re
import os
from lxml.etree import ElementTree as ET
import senseTk.extension.functional as F


class Det(object):

    OBJECT_PED = 1
    OBJECT_OTHER = 2
    OBJECT_VEHICLE = 3

    def __init__(self, x1, y1, w, h, cls=None, confidence=1.,
                 uid=-1, fr=-1, status=-1):
        self._x1 = x1
        self._y1 = y1
        self._w = w
        self._h = h
        self.label = cls
        self.conf = confidence
        self.uid = uid
        self.fr = fr
        self.status = status

    @property
    def w(self):
        return self._w

    @w.setter
    def w(self, w):
        self._w = w

    @property
    def h(self):
        return self._h

    @h.setter
    def h(self, h):
        self._h = h

    @property
    def x1(self):
        return self._x1

    @x1.setter
    def x1(self, x1):
        self._x1 = x1

    @property
    def x2(self):
        return self._x1 + self._w

    @x2.setter
    def x2(self, x2):
        self._w = x2 - self._x1

    @property
    def y1(self):
        return self._y1

    @y1.setter
    def y1(self, y1):
        self._y1 = y1

    @property
    def y2(self):
        return self._y1 + self._h

    @y2.setter
    def y2(self, y2):
        self._h = y2 - self._y1

    @property
    def cx(self):
        return self._x1 + self._w/2

    @cx.setter
    def cx(self, cx):
        self._x1 = cx - self._w/2

    @property
    def cy(self):
        return self._y1 + self._h/2

    @cy.setter
    def cy(self, cy):
        self._y1 = cy - self._h/2

    # def __setattr__(self, x, y):
    #     if not self.__free__ and (x=='x2' or x=='y2' or x=='cx' or x=='cy'):
    #         raise Exception('cannot modify infered properties')
    #     super(Det, self).__setattr__(x, y)
    #     if x=='x1' or x=='y1' or x=='w' or x=='h':
    #         self.__free__ = True
    #         self.x2 = self.x1 + self.w
    #         self.y2 = self.y1 + self.h
    #         self.cx = (self.x1 + self.x2)/2
    #         self.cy = (self.y1 + self.y2)/2
    #         self.__free__ = False

    '''
    def area(self):
        w = max(self.w, 0)
        h = max(self.h, 0)
        return w*h
    '''

    def area(self):
        return F.c_area(self.w, self.h)

    '''
    def intersection(self, o):
        mx1 = max(self.x1, o.x1)
        my1 = max(self.y1, o.y1)
        mx2 = min(self.x2, o.x2)
        my2 = min(self.y2, o.y2)
        ix = (mx2 - mx1) if (mx2 - mx1 > 0) else 0
        iy = (my2 - my1) if (my2 - my1 > 0) else 0
        return ix*iy
    '''

    def intersection(self, o):
        return F.c_intersection(self.x1, self.y1, self.w, self.h, o.x1, o.y1, o.w, o.h)

    '''
    def union(self, o):
        return self.area() + o.area() - self.intersection(o)
    '''

    def union(self, o):
        return F.c_union(self.x1, self.y1, self.w, self.h, o.x1, o.y1, o.w, o.h)

    '''
    def iou(self, o):
        intersect = self.intersection(o)
        return intersect * 1. / (self.area() + o.area() - intersect);
    '''

    def iou(self, o):
        return F.c_iou(self.x1, self.y1, self.w, self.h, o.x1, o.y1, o.w, o.h)

    def lt(self, ox=0, oy=0, trim=True):
        if trim:
            return (int(self.x1 + ox), int(self.y1 + oy))
        else:
            return ((self.x1 + ox), (self.y1 + oy))

    def rb(self, ox=0, oy=0, trim=True):
        if trim:
            return (int(self.x1 + self.w + ox), int(self.y1 + self.h + oy))
        else:
            return ((self.x1 + self.w + ox), (self.y1 + self.h + oy))

    def _trim(self, sz=None, toInt=True):
        if sz is not None:
            w, h = sz
            x1, y1, x2, y2 = self.x1, self.y1, self.x2, self.y2
            x1 = max(x1, 0)
            y1 = max(y1, 0)
            x2 = min(w, x2)
            y2 = min(h, y2)
            self.x1 = x1
            self.y1 = y1
            self.w = max(x2 - x1, 0)
            self.h = max(y2 - y1, 0)
        if toInt:
            self.x1, self.y1, self.w, self.h = map(int, self.toList())
        return self

    def trim(self, sz=None, toInt=True):
        ret = copy.copy(self)
        return ret._trim(sz, toInt=toInt)

    def _astype(self, dtype):
        self.x1, self.y1, self.w, self.h = map(dtype, self.toList())
        return self

    def copy(self):
        return copy.copy(self)

    def astype(self, dtype):
        ret = copy.copy(self)
        return ret._astype(dtype)

    def __mul__(self, a):
        tmp = copy.copy(self)
        if isinstance(a, float) or isinstance(a, int):
            nw = self.w*a
            nh = self.h*a
            cx = self.cx
            cy = self.cy
            tmp.x1 = cx - nw/2
            tmp.y1 = cy - nh/2
            tmp.w = nw
            tmp.h = nh
        return tmp

    def __repr__(self):
        return 'Det [%d,%d,%.2f,%.2f,%.2f,%.2f,%.3f,%s,%d,-1]' %\
            (self.fr, self.uid, self.x1, self.y1, self.w, self.h,
             self.conf, str(self.label), self.status)

    def __str__(self):
        return '%d,%d,%.2f,%.2f,%.2f,%.2f,%.3f,%s,%d,-1' %\
            (self.fr, self.uid, self.x1, self.y1, self.w, self.h,
             self.conf, str(self.label), self.status)

    def toList(self):
        return [self.x1, self.y1, self.w, self.h]

    def toTuple(self):
        return (self.x1, self.y1, self.w, self.h)


class TrackSet(object):  # general Det of Video

    min_fr = 1000000000
    max_fr = -1

    @staticmethod
    def readline(row):
        arr = re.split('[,\\s]+', row.strip())
        if len(arr) == 7:
            return TrackSet.readline_MOTdet(row)
        if len(arr) == 8:
            return TrackSet.readline_label(row)
        if len(arr) == 9:
            return TrackSet.readline_groundtruth(row)
        if len(arr) == 10:
            return TrackSet.readline_result(row)
        raise Exception('Unknown Format')

    @staticmethod
    def readline_label(row):
        return TrackSet.formatline(row, 'fr.i id.i x1 y1 w h cf la.s')

    @staticmethod
    def readline_detect(row):
        return TrackSet.formatline(row, 'fr.i id.i x1 y1 w h cf la.s -1 -1')

    @staticmethod
    def readline_MOTdet(row):
        return TrackSet.formatline(row, 'fr.i id.i x1 y1 w h cf')

    @staticmethod
    def readline_result(row):
        return TrackSet.formatline(row, 'fr.i id.i x1 y1 w h cf st.i la.s -1')

    @staticmethod
    def readline_groundtruth(row):
        return TrackSet.formatline(row, 'fr.i id.i x1 y1 w h st.i la.i cf')

    @staticmethod
    def formatline(row, formatter):
        items = re.split('[,\\s]+', formatter.strip())
        row = re.split('[,\\s]+', row.strip())
        if len(items) != len(row):
            raise Exception('Formatter does not match line: %d vs %d' %
                            (len(items), len(row)))
        tmp = {}
        for k, v in zip(items, row):
            tp = float
            if '.' in k:
                k, t = k.split('.')
                if t == 'i':
                    tp = int
                if t == 's':
                    tp = str
                if t == 'f':
                    tp = float
            tmp[k] = tp(v)
        if 'x1' in tmp and 'w' in tmp:
            x1 = tmp['x1']
            y1 = tmp['y1']
            w = tmp['w']
            h = tmp['h']
        if 'cx' in tmp and 'w' in tmp:
            w = tmp['w']
            h = tmp['h']
            x1 = tmp['cx'] - w/2
            y1 = tmp['cy'] - h/2
        if 'x1' in tmp and 'x2' in tmp:
            x1 = tmp['x1']
            y1 = tmp['y1']
            w = tmp['x2'] - x1
            h = tmp['y2'] - y1
        kwargs = {}
        if 'fr' in tmp:
            kwargs['fr'] = tmp['fr']
        if 'id' in tmp:
            kwargs['uid'] = tmp['id']
        if 'la' in tmp:
            kwargs['cls'] = tmp['la']
        if 'cf' in tmp:
            kwargs['confidence'] = tmp['cf']
        if 'st' in tmp:
            kwargs['status'] = tmp['st']
        res = Det(x1, y1, w, h, **kwargs)
        return res

    def dump(self, fd, formatter='MOT16', filter=None):
        if formatter == 'MOT16':
            formatter = 'fr.i,id.i,x1,y1,w,h,-1,st.i,-1,-1'
        items = re.split('[,\\s]+', formatter.strip())
        for i in self.frameRange():
            one = self[i]
            for dt in one:
                if filter is not None and not filter(dt):
                    continue
                tmp = ''
                for i, k in enumerate(items):
                    tp = str
                    if '.' in k:
                        k, t = k.split('.')
                        if t == 'i':
                            tp = int
                        if t == 's':
                            tp = str
                        if t == 'f':
                            tp = float
                    v = k
                    if k == 'fr':
                        v = dt.fr
                    if k == 'id':
                        v = dt.uid
                    if k == 'x1':
                        v = dt.x1
                    if k == 'x2':
                        v = dt.x2
                    if k == 'y1':
                        v = dt.y1
                    if k == 'y2':
                        v = dt.y2
                    if k == 'cx':
                        v = dt.cx
                    if k == 'cy':
                        v = dt.cy
                    if k == 'w':
                        v = dt.w
                    if k == 'h':
                        v = dt.h
                    if k == 'la':
                        v = dt.label
                    if k == 'st':
                        v = dt.status
                    if k == 'cf':
                        v = dt.conf
                    v = tp(v)
                    if i == 0:
                        tmp = tmp + '%s' % v
                    else:
                        tmp = tmp + ',%s' % v
                fd.write(tmp+'\n')

    def toJson(self, frfirst=False, filter=None):
        js = {}
        if frfirst:
            for i in self.frameRange():
                tmp = {}
                js['%06d' % i] = tmp
                one = self[i]
                for it in one:
                    if filter is not None and not filter(it):
                        continue
                    tmp['%02d' % it.uid] = [it.x1, it.y1, it.x2, it.y2]

        else:
            for one in self.allId():
                tmp = {}
                js['%02d' % one] = tmp
                one = self(one)
                for i in one.frameRange():
                    if len(one[i]):
                        it = one[i][0]
                        if filter is not None and not filter(it):
                            continue
                        tmp['%06d' % i] = [it.x1, it.y1, it.x2, it.y2]
        return js

    def _load_txt(self, f, dealer, filter, formatter):
        rows = f.readlines()
        for row in rows:
            if dealer is None:
                if formatter is None:
                    D = self.readline(row)
                else:
                    D = self.formatline(row, formatter)
            else:
                D = dealer(row)
            if D is None or filter is not None and not filter(D):
                continue
            # print type(D)
            if isinstance(D, Det) == False:
                # print D
                fr, uid, x1, y1, w, h, label, conf = D
                D = Det(x1, y1, w, h, cls=label, confidence=conf,
                        fr=fr, uid=uid)
            self.append_data(D)

    def _load_xml(self, f, filter_):

        def best_match(x):
            val = int(x) if x.isdigit() else x
            if isinstance(val, str):
                try:
                    float(val)
                    val = float(val)
                except ValueError as e:
                    pass
            return val

        anno = ET(file=f).getroot()
        common_kv = {}
        objs = []
        for obj in anno.iterfind('./'):
            if obj.tag == 'object':
                objs.append(obj)
            if obj.tag == 'size':
                common_kv[obj.tag] = dict(
                    width=int(obj.find('width').text.strip()),
                    height=int(obj.find('height').text.strip()),
                )
            else:
                common_kv[obj.tag] = best_match(obj.text.strip())
        if isinstance(common_kv.get('filename', ''), int):
            common_kv['fr'] = common_kv.get('filename')
        for obj in objs:
            box = obj.find('bndbox')
            x1 = float(box.find('xmin').text)
            x2 = float(box.find('xmax').text)
            y1 = float(box.find('ymin').text)
            y2 = float(box.find('ymax').text)
            w = x2 - x1 + 1
            h = y2 - y1 + 1
            d = Det(x1, y1, w, h)
            for k, v in common_kv.items():
                setattr(d, k, v)
            for one in obj.iterfind('./'):
                if one.tag == 'name':
                    d.label = one.text
                elif one.tag == 'trackid' or one.tag == 'id':
                    d.uid = int(one.text)
                elif one.tag == 'confidence':
                    d.conf = float(one.text)
                elif one.tag == 'frame' or one.tag == 'frameindex':
                    d.fr = int(one.text)
                else:
                    val = best_match(one.text.strip())
                    setattr(d, one.tag, val)
            if d is None or filter_ is not None and not filter_(d):
                continue
            self.append_data(d)

    def __init__(self, fn=None, dealer=None, filter=None, formatter=None):
        self.__frd = {}
        self.__idd = {}
        self.__cache_id = {}
        self.__cache_fr = {}
        self.__n_id = 0
        if fn is not None:
            if os.path.isdir(fn):
                fns = [os.path.join(fn, i) for i in os.listdir(fn)]
            else:
                fns = [fn]
            for fn in fns:
                with open(fn) as f:
                    if os.path.splitext(fn)[-1] == '.xml':
                        self._load_xml(f, filter)
                    else:
                        self._load_txt(f, dealer, filter, formatter)

    def __getitem__(self, index):
        if isinstance(index, int):
            if index in self.__cache_fr:
                return self.__cache_fr[index]
            if index in self.__frd:
                ret = list(self.__frd[index].values())
                self.__cache_fr[index] = ret
                return ret
            else:
                return []
        if isinstance(index, slice):
            res = self.__class__()
            for i in range(*(index.indices(self.max_fr+1))):
                if i in self.__frd:
                    for one in self.__frd[i].values():
                        res.append_data(one.copy())
            return res
        raise Exception('index must be integer or slice. NOT  %s' % str(index))

    def __setitem__(self, index, val):
        if isinstance(index, int):
            for one in list(self.__frd.get(index, {}).values()):
                self.delete(one)
            if val is None:
                pass
            elif isinstance(val, list):
                for one in val:
                    if one.fr == index:
                        self.append_data(one)
            elif val.fr == index:
                self.append_data(val)
            self.max_fr = max(self.max_fr, index)
            self.min_fr = min(self.min_fr, index)
        elif isinstance(index, slice):
            for i in range(*(index.indices(self.max_fr+1))):
                for one in list(self.__frd.get(i, {}).values()):
                    self.delete(one)
            if val is None:
                pass
            elif isinstance(val, self.__class__):
                mxf = max(self.max_fr, val.max_fr)
                for i in range(*(index.indices(mxf+1))):
                    for one in val[i]:
                        self.append_data(one)
                    self.max_fr = max(self.max_fr, i)
                    self.min_fr = min(self.min_fr, i)
            else:
                raise ValueError(
                    'Only TrackSet can be assigned to TrackSet segment.')
        else:
            raise Exception(
                'index must be integer or slice. NOT  %s' % str(index))

    def frameRange(self):
        return range(self.min_fr, self.max_fr+1)

    def allPed(self):
        return self.__idd.keys()

    def allId(self):
        return self.__idd.keys()

    def allFr(self):
        return self.__frd.keys()

    @property
    def __nxt_id(self):
        self.__n_id += 1
        return self.__n_id

    def append_data(self, D):
        if D.uid == -1:
            D.uid = - self.__nxt_id
        if D.uid not in self.__idd:
            self.__idd[D.uid] = {}
        self.__idd[D.uid][D.fr] = D
        if D.fr not in self.__frd:
            self.__frd[D.fr] = {}
        self.__frd[D.fr][D.uid] = D
        self.min_fr = min(self.min_fr, D.fr)
        self.max_fr = max(self.max_fr, D.fr)
        if D.uid in self.__cache_id:
            self.__cache_id[D.uid].append_data(D)
        if D.fr in self.__cache_fr:
            self.__cache_fr[D.fr].append(D)

    def count(self):
        return sum([len(i) for i in self.__frd.values()])

    def fr_count(self, frIndex=None):
        if frIndex is None:
            return len(self.__frd)
        else:
            return len(self.__frd.get(frIndex, {}))

    def id_count(self, idIndex=None):
        if idIndex is None:
            return len(self.__idd)
        else:
            return len(self.__idd.get(idIndex, {}))

    def delete(self, d):
        if isinstance(d, list) or isinstance(d, tuple):
            uid, fr = d
        else:
            uid, fr = d.uid, d.fr
        if fr in self.__frd:
            if uid in self.__frd[fr]:
                del self.__frd[fr][uid]
        if uid in self.__idd:
            if fr in self.__idd[uid]:
                del self.__idd[uid][fr]
        if fr in self.__cache_fr:
            del self.__cache_fr[fr]
        if uid in self.__cache_id:
            self.__cache_id[uid].delete(d)
        if len(self.__frd[fr]) == 0:
            del self.__frd[fr]
            if fr in self.__cache_fr:
                del self.__cache_fr[fr]
        if len(self.__idd[uid]) == 0:
            del self.__idd[uid]
            if uid in self.__cache_id:
                del self.__cache_id[uid]

    def __call__(self, ind):
        if ind in self.__cache_id:
            return self.__cache_id[ind]
        if ind in self.__idd:
            ret = self.__class__()
            for one in self.__idd[ind].values():
                ret.append_data(one)
            self.__cache_id[ind] = ret
            return ret
        else:
            return None

    def __add__(self, o):
        assert isinstance(o, TrackSet), 'Unsupported operand type %s' % type(o)
        ret = self[:]
        for f in o.__frd:
            for d in o.__frd[f].values():
                ret.append_data(d)
        return ret

    def __iadd__(self, o):
        assert isinstance(o, TrackSet), 'Unsupported operand type %s' % type(o)
        for f in o.__frd:
            for d in o.__frd[f].values():
                self.append_data(d)
        return self
