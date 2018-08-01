#!/usr/bin/python
# -*- coding: utf8 -*-
#########################################################################
# File Name: scripts/gtsearch.py
# Author: Toka
# mail: fengweitao@sensetime.com
# Created Time: 2018年08月01日 星期三 18时04分27秒
#########################################################################
from senseTk.magic import *
from senseTk.tracking.mot import make_dataset
from time import sleep
if __name__=='__main__':
    # __author__ == '__toka__'
    root = '/home/sensetime/data/sdk_dataset/testcase'
    gtS = gtSearcher(root, default_gt_search_config)
    for k, v in gtS():
    	print k, v
    gtS.saveState('./a.rec')
    del gtS
    gtS = None
    sleep(15) # wait to add new gt dir
    gg = gtSearcher(root, default_gt_search_config).loadState('./a.rec')
    make_dataset(gg, '/home/sensetime/data/jjjjffff')
