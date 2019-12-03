#!/usr/bin/python
# -*- coding: utf8 -*-
#########################################################################
# File Name: senseTk/tracking/mot/dataset.py
# Author: Toka
# mail: fengweitao@sensetime.com
# Created Time: 2018年08月01日 星期三 18时20分41秒
#########################################################################
import logging
import os
import cv2
from senseTk.magic import *
from senseTk.common import *
import json
import re

USERLOG = logging.DEBUG + 5
logging.addLevelName(USERLOG, 'USER')
da_formatter = logging.Formatter('%(asctime)s - %(name)s %(levelname)s] %(message)s')

da_stream_handler = logging.StreamHandler()
da_stream_handler.setLevel(USERLOG)
da_stream_handler.setFormatter(da_formatter)
logger = logging.getLogger(__name__)
logger.addHandler(da_stream_handler)
logger.setLevel(USERLOG)


def make_lines(*args, **sps):
	res = ''
	for i in args:
		if isinstance(i,tuple):
			t = ''
			for j in i:
				t = t + str(j) + sps['sp']
			i = t[:-1]
		res += str(i) + '\n'
	return res

def parseFMT(x):
	k = re.split(r'\s+', x.strip())
	res = {}
	for _, i in enumerate(k):
		res[i] = _
	pat = 'xy1wh'
	if 'x1' not in res:
		pat = 'cxywh'
	if 'w' not in res and pat=='xy1wh':
		pat = 'xy1xy2'
	return pat, res

def printConf(c):
	for i in c:
		logger.info('%s : %s'%(i, c[i]))

def loadConfig(x):
	if isinstance(x, str):
		conf = json.load(open(x))
	else:
		conf = x
	# if 'search_dir' not in conf:
	# 	raise Exception('no search_dir found.')
	# if 'dataset_dir' not in conf:
	# 	raise Exception('no dataset_dir found.')
	if 'Task_Note' not in conf:
		conf['Task_Note'] = 'task'
		# print 'set Task_Note to [task]'
	if 'Video_Ext' not in conf:
		conf['Video_Ext'] = []
	if 'Label_Ext' not in conf:
		conf['Label_Ext'] = []
	if 'Prefix' not in conf:
		conf['Prefix'] = 'undefine'
		# print 'set Prefix to [undefine]'
	if 'fmt' not in conf:
		conf['fmt'] = 'fr id x1 y1 w h conf cls'
	conf['location'], conf['fmt'] = parseFMT(conf['fmt'])
	if 'index0' not in conf:
		conf['index0'] = 1
		# print 'assume 0-indexed'
	if 'delimiter' not in conf:
		conf['delimiter'] = ' '
		# print 'assume delimiter \' \''
	printConf(conf)
	return conf

def make_dataset(data, destination, args = None):
	if args is None:
		args = default_gt_search_config
	if isinstance(data, str):
		args = loadConfig(args)
		sa = gtSearcher(data, args)
		data = sa()
	if isinstance(data, gtSearcher):
		sa = data
		args = loadConfig(sa.config)
		data = sa()
	cnt = 0
	try:
		os.mkdir(destination)
	except:
		pass
	for k, v in data:
		logger.info('%s %s'%(str(k), str(v)))
		if len(v[2])==0:
			logger.warn('%s has no label file!'%v[1])
		if len(v[2])==0 or v[1]=='-': continue
		one_path = destination+'/'+v[0]+'/'
		try:
			os.mkdir(one_path)
			os.mkdir(one_path+'gt')
			os.mkdir(one_path+'img1')
		except:
			pass
		os.system('cp %s %s'%(v[1], one_path+v[0]+'.'+v[1].split('.')[-1]))
		fd = open(one_path+'info.txt', 'w')
		fd.write(v[0]+'.'+v[1].split('.')[-1]+'\n')
		fd.write(v[0]+'\n')
		fd.write(v[1]+'\n')
		for x in v[2]:
			fd.write(x+'\n')
		fd.close()
		fd = open(one_path+'seqinfo.ini', 'w')
		vid = VideoClipReader(v[1])
		seqlen = int(vid.length())
		imW, imH = vid.ImgSize()
		fps = vid.fps()
		logger.info('seqlen: %d w %d h %d fps: %g'%(seqlen, imW, imH, fps))
		vid.release()
		fd.write(
			make_lines(
				'[Sequence]',
				'name=%s'%v[0],
				'imDir=img1',
				'frameRate=%g'%fps,
				'seqLength=%d'%seqlen,
				'imWidth=%d'%imW,
				'imHeight=%d'%imH,
				'imExt=.jpg'
			)
		)
		fd.close()
		allrow = []
		k = len(v[2])
		fmt = args['fmt']
		fr_c = args['index0']!=0
		for gid, i in enumerate(v[2]):
			fd = open(i)
			rows = fd.readlines()
			for i in rows:
				i = i.strip()
				i = re.split(args['delimiter'], i)
				fr = str(int(i[fmt['fr']])+fr_c)
				uid = str(int(i[fmt['id']])*k+gid)
				if 'cls' not in fmt:
					cl = str(gid+1)
				else:
					cl = i[fmt['cls']]
				if 'conf' not in fmt:
					conf = str(1)
				else:
					conf = i[fmt['conf']]
				if args['location']=='cxywh':
					cx = str(float(i[fmt['cx']]))
					cy = str(float(i[fmt['cy']]))
					w = str(float(i[fmt['w']]))
					h = str(float(i[fmt['h']]))
					x1 = str(cx - w/2.)
					y1 = str(cy - h/2.)
				if args['location']=='xy1wh':
					x1 = str(float(i[fmt['x1']]))
					y1 = str(float(i[fmt['y1']]))
					w = str(float(i[fmt['w']]))
					h = str(float(i[fmt['h']]))
				if args['location']=='xy1xy2':
					x1 = str(float(i[fmt['x1']]))
					y1 = str(float(i[fmt['y1']]))
					x2 = str(float(i[fmt['x2']]))
					y2 = str(float(i[fmt['y2']]))
					w = str(x2 - x1)
					h = str(y2 - y1)
				allrow.append((fr,uid,x1,y1,w,h,'1',cl,conf))
			fd.close()
		fd = open(one_path+'gt/gt.txt', 'w')
		fd.write(make_lines(*allrow, sp = ','))
		fd.close()
		cnt += 1
	logger.info('all %d videos'%cnt)
