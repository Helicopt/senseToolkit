#!/usr/bin/python
# -*- coding: utf8 -*-
#########################################################################
# File Name: senseTk/magic/gtSearcher.py
# Author: Toka
# mail: fengweitao@sensetime.com
# Created Time: 2018年08月01日 星期三 17时05分21秒
#########################################################################
import sys
import os
from math import *
import random
import cv2
import re
import json

def match(strlist, content):
	for one in strlist:
		if one in content:
			return True
	return False

def splMatch(x, y):
    pos = y.find(x)
    if pos<0: return False
    be = pos-1
    en = pos+len(x)
    def ctyp(x):
        if ord(x)>=ord('0') and ord(x)<=ord('9'): return 1
        if ord(x)>=ord('a') and ord(x)<=ord('z'): return 2
        if ord(x)>=ord('A') and ord(x)<=ord('Z'): return 2
        return 0
    chDiff = lambda x, y: ctyp(x)!=ctyp(y)
    if (be<0 or chDiff(y[be], x[0])) and (en>=len(y) or chDiff(y[en], x[-1])):
            return True
    return False

global videoExt, default_gt_search_config

videoExt = ['avi', 'mp4', 'flv']

default_gt_search_config = \
{
	# "search_dir": "./origin",
	# "dataset_dir": "./fine",
	"Task_Note": ["task"],
	"Video_Ext": ["MOV", "flv", "avi", "mp4"],
	"Label_Ext": ["gt"],
	"Prefix": "POI",
	"fmt": "fr id x1 y1 w h conf cls",
	"delimiter": " "
}

def make_gt_config(seqName = '', fmt = '', delimiter = ''):
	ret = {}
	ret.update(default_gt_search_config)
	if seqName!='':
		ret['Prefix'] = seqName
	if fmt!='':
		ret['fmt'] = fmt
	if delimiter!='':
		ret['delimiter'] = delimiter
	return ret

class gtSearcher(object):
	"""docstring for Searcher"""
	def __init__(self, root = '.', config = default_gt_search_config):
		super(gtSearcher, self).__init__()
		self.root = root
		self.fdict = {}
		self.uuid = 0
		self.tmpid = 0
		self.config = config
		if config is None:
			raise Exception('empty config file')

	def reset(self):
		self.fdict = {}
		self.uuid = 0
		self.tmpid = 0
		return self

	def loadState(self, fn):
		with open(fn) as f:
			self.fdict = json.load(f)
			self.uuid, self.tmpid = self.fdict['_param_']
			del self.fdict['_param_']
		return self

	def saveState(self, fn):
		with open(fn, 'w') as f:
			self.fdict['_param_'] = [self.uuid, self.tmpid]
			json.dump(self.fdict, f, indent = 2, sort_keys = True)
		return self

	def __new(self):
		self.uuid += 1
		return self.uuid

	def __tmp(self):
		self.tmpid += 1
		return self.tmpid

	def __search(self, path, prefix = ''):
		if os.path.isdir(path):
			files = sorted(os.listdir(path))
			for i in files:
				fn = path+'/'+i
				if os.path.isdir(fn):
					if i[0]=='.': # hidden dirs will not search
						continue
					if match(self.config['Task_Note'], i.lower()): # new task
						self.__search(fn, prefix + i + '!!')
					else:
						self.__search(fn, prefix)
				else:
					if i.split('.')[-1].lower() in (videoExt + self.config['Video_Ext']): # video file
						nm = prefix+i[:-len(i.split('.')[-1])-1]
						if nm in self.fdict: # already exists
							if self.fdict[nm][1]=='-': # only label file
								new_label = self.__new()
								self.fdict[nm] = ('%s-%03d'%(self.config['Prefix'], new_label), fn, self.fdict[nm][2])
							else: # duplicate video, replace it
								self.fdict[nm] = (self.fdict[nm][0], fn, self.fdict[nm][2])
						else: # not exist
							new_label = self.__new()
							self.fdict[nm] = ('%s-%03d'%(self.config['Prefix'], new_label), fn, [])
					if i.split('.')[-1].lower() in (['txt'] + self.config['Label_Ext']): # label file
						nm = prefix+i[:-len(i.split('.')[-1])-1]
						if nm in self.fdict:
							if fn not in self.fdict[nm][2]:
								self.fdict[nm][2].append(fn) # already found video
						else: # cache label file
							new_label = self.__tmp()
							self.fdict[nm] = ('-%03d'%(-new_label), '-', [fn])
	def __merge(self):
		unMerge = []
		for one, v in self.fdict.items():
			if v[1]=='-':
				unMerge.append(one)
		for one, v in self.fdict.items():
			if v[1]!='-':
				i = 0
				while i<len(unMerge):
					two = unMerge[i]
					item = self.fdict[two]
					if splMatch(one.split('!!')[-1], two.split('!!')[-1]) and ''.join(one.split('!!')[:-1])==''.join(two.split('!!')[:-1]):
						v2 = map(str,list(set(map(unicode, v[2]+item[2]))))
						self.fdict[one] = (v[0], v[1], v2)
						v = self.fdict[one]
						del unMerge[i]
						continue
					i += 1
		for one, v in self.fdict.items():
			if v[1]=='-':
				del self.fdict[one]

	def search(self):
		# self.fdict = {}
		self.__search(self.root)
		self.__merge()
		return self.fdict

	def __call__(self):
		return sorted(self.search().items(), key=lambda x: x[0])
