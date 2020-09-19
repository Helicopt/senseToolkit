#!/usr/bin/python
# -*- coding: utf8 -*-
#########################################################################
# File Name: magic/bigBitset.py
# Author: Toka
# mail: fengweitao@sensetime.com
# Created Time: 2018年07月31日 星期二 18时28分58秒
#########################################################################

class BigBitSet(object):

    def __init__(self, p):
        self.n = p+7 >> 3
        self.data = bytearray(self.n)

    def set(self, ind):
        p = ind >> 3
        if p >= self.n or ind < 0:
            return
        r = ind & 7
        b = 1 << r
        self.data[p] |= b

    def unset(self, ind):
        p = ind >> 3
        if p >= self.n or ind < 0:
            return
        r = ind & 7
        b = 0xff ^ (1 << r)
        self.data[p] &= b

    def __getitem__(self, ind):
        p = ind >> 3
        if p >= self.n or ind < 0:
            return None
        r = ind & 7
        b = 1 << r
        res = self.data[p] & b
        return res > 0

    def __setitem__(self, ind, val):
        if val != 0:
            self.set(ind)
        else:
            self.unset(ind)

    def __len__(self):
        return self.n << 3

    def reset(self, v=0x00):
        for i in range(self.n):
            self.data[i] = v

    def save(self, bfile=None):
        if bfile is not None:
            bfile.write(self.data)
            self.src = bfile.name
        else:
            if 'src' in self.__dict__:
                fd = open(self.__dict__['src'], 'wb')
                fd.write(self.data)
                fd.close()

    def load(self, bfile):
        self.src = bfile.name
        self.data = bytearray(bfile.read())
        self.n = len(self.data)
