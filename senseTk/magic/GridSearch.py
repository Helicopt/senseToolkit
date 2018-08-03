#!/usr/bin/python
# -*- coding: utf8 -*-
#########################################################################
# File Name: magic/GridSearch.py
# Author: Toka
# mail: fengweitao@sensetime.com
# Created Time: 2018年07月31日 星期二 18时27分19秒
#########################################################################
import os
import json
import threading
from subprocess import Popen, PIPE
from math import *
from time import sleep, time
import collections
import random
import tempfile
import re
import logging

USERLOG = logging.DEBUG + 5
logging.addLevelName(USERLOG, 'USER')
gridsearch_formatter = logging.Formatter('%(asctime)s - %(name)s {%(thread)d} %(levelname)s] %(message)s')

gridsearch_stream_handler = logging.StreamHandler()
gridsearch_stream_handler.setLevel(USERLOG)
gridsearch_stream_handler.setFormatter(gridsearch_formatter)

from bigBitset import BigBitSet

def OrderedDict(x = None):
	if x is None:
		return collections.OrderedDict()
	else:
		return collections.OrderedDict(sorted(x.items(), key = lambda x: x[0]))

def frange(l,r,s):
	res = []
	d = log10(s)
	if d<0:
		d = int(ceil(-d))
	else:
		d = int(floor(d))
	while l<=r:
		res.append(round(l,d))
		l+=s
	return res

class worker(threading.Thread):
	def __init__(self, task, argv):
		super(worker, self).__init__()
		self.task = task
		self.argv = argv
		self.holder = argv[0]
	def run(self):
		ret = self.task[0](*self.argv)
		ind = self.argv[2]
		res = self.task[1](self.holder, ind, ret)
		# global llock, bb, rec_json
		self.holder.llock.acquire()
		self.holder.done+=1
		self.holder.rec_json[str(ind)] = OrderedDict({'rec': OrderedDict(res), 'params': self.argv[1]})
		self.holder.bb[ind] = 1
		bak = self.holder.recfile+'.bak'
		fd = open(bak, 'w')
		json.dump(self.holder.rec_json, fd, indent = 2, sort_keys = True)
		fd.close()
		os.system('mv %s %s'%(bak, self.holder.recfile))
		self.holder.bb.save()
		pstr = 'progress: %.2f %% ( %d / %d )'%(self.holder.done*100./self.holder.tot,
			self.holder.done, self.holder.tot)
		self.holder.logger.info(pstr)
		self.holder.llock.release()

def gen_params(st, p):
	l = len(st)
	res = []
	for i in range(l):
		k = p%st[i][0]
		res.append(k)
		p/=st[i][0]
	return res

def gen_code(st, c):
	b = 1
	res = 0
	l = len(st)
	for i in range(l):
		res += c[i]*b
		b*=st[i][0]
	return res

class gridSearcher(object):

	def __init__(self, name = None, params = None, run_ = None, rec_ = None, eva_ = None, state = None):
		if name is None:
			name = 'GTask_%d'%int(time())
		self.name = str(name)
		self.p = OrderedDict(params) if params is not None else None
		self.run_func = run_
		self.rec_func = rec_
		self.eva_func = eva_
		self.cmp = cmp
		self.state = state
		self.bb = None
		self.llock = threading.Lock()
		self.rec_json = None
		self.logger = logging.getLogger(self.name)
		self.logger.addHandler(gridsearch_stream_handler)
		self.logger.setLevel(USERLOG)
		self.max_job = 64
		self.done = 0
		self.tot = 1

	def set_run(self, f):
		self.run_func = f
		return self

	def set_eval(self, f):
		self.eva_func = f
		return self

	def set_rec(self, f):
		self.rec_func = f
		return self

	def set_state(self, s):
		self.state = s
		return self

	def set_params(self, p):
		self.p = OrderedDict(p)
		return self

	def set_cmp(self, f):
		self.cmp = f
		return self

	def set_max_job(self, cnt):
		if cnt<=0:
			self.max_job = 64
		else:
			self.max_job = cnt

	def log(self, msg, *args):
		self.logger.log(USERLOG, msg%args)

	def __call__(self):
		return self.execute()

	def execute(self):
		if not isinstance(self.p, dict):
			raise Exception('Invalid params.')
		if not callable(self.run_func):
			raise Exception('run funciton is not callable.')
		if not callable(self.eva_func):
			raise Exception('eval funciton is not callable.')
		if not callable(self.rec_func):
			raise Exception('rec funciton is not callable.')
		if not callable(self.cmp):
			raise Exception('compare funciton is not callable.')
		return self.__grid_search()

	def __grid_search(self):
		self.logger.info('Mission [%s] start.'%self.name)
		st = []
		nm = []
		self.tot = 1

		for k,v in self.p.items():
			r = frange(*v)
			cnt = len(r)
			st.append((cnt,r))
			nm.append(k)
			self.logger.info('%16s : %s all %d values'%(k, str(r), cnt))
			self.tot*=cnt
		self.logger.info('%d situations in total'%self.tot)
		if self.state is not None:
			bits = self.state['bits']
			recfile = self.state['record']
		else:
			bits = './%s.bits'%self.name
			recfile = './%s.rec'%self.name
		self.bits = bits
		self.recfile = recfile
		if not os.path.isfile(bits):
			self.bb = BigBitSet(self.tot)
			fd = open(bits, 'wb')
			self.bb.save(fd)
			fd.close()
		else:
			self.bb = BigBitSet(0)
			self.bb.load(open(bits,'rb'))
		if not os.path.isfile(recfile):
			self.rec_json = OrderedDict()
			fd = open(recfile, 'w')
			json.dump(self.rec_json,fd, indent=2, sort_keys = True)
			fd.close()
		else:
			self.rec_json = OrderedDict(json.load(open(recfile, 'r')))
		self.done = 0
		ptr = -1
		best = None
		bid = -1
		for i in range(self.tot):
			if self.bb[i]:
				self.done+=1
				tmp = self.rec_func(self, self.rec_json[str(i)]['rec'])
				if best is None or self.cmp(tmp, best)<0:
					best = tmp
					bid = i
			elif ptr<0: ptr = i
		if bid!=-1: ptr = bid
		while True:
			pstr = 'progress: %.2f %% ( %d / %d )'%(self.done*100./self.tot,
				self.done, self.tot)
			self.logger.info(pstr)
			if os.path.isfile('./stop.signal.%s'%self.name):
				break
			if self.done>=self.tot:
				break
			while self.bb[ptr]:
				ptr+=1
				ptr%=self.tot
			p = gen_params(st, ptr)
			len_p = len(p)
			p_p = range(len_p)
			random.shuffle(p_p)
			for i in p_p:
				cc = st[i][0]
				mx = None
				mi = -1
				for j in range(0,cc):
					p[i] = j
					_ = gen_code(st, p)
					if not self.bb[_]:
						real_p = [st[k][1][p[k]] for k in range(len_p)]
						merge_p = OrderedDict({nm[k]:real_p[k] for k in range(len_p)})
						
						t = worker(task = (self.run_func, self.eva_func), argv = (self, merge_p, _))
						t.setDaemon(True)
						t.start()
				main_t = threading.currentThread()
				for t in threading.enumerate():
					if t is main_t:
						continue
					t.join()
				bak = recfile+'.bak'
				fd = open(bak, 'w')
				json.dump(self.rec_json, fd, indent = 2, sort_keys = True)
				fd.close()
				os.system('mv %s %s'%(bak, recfile))
				self.bb.save()
				for j in range(0, cc):
					p[i] = j
					_ = gen_code(st, p)
					if not self.bb[_]:
						self.logger.error('Fatal Error: thread broken.')
						exit(233)
					tmp = self.rec_func(self, self.rec_json[str(_)]['rec'])
					if mx is None or self.cmp(tmp, mx)<0:
						mx = tmp
						mi = j
				p[i] = mi
				if best is None or self.cmp(mx,  best)<0:
					best = mx
					bid = gen_code(st, p)
					self.logger.info('update best: %.3f, task_id %d'%(best, bid))
				self.logger.info('now best: %.3f, task_id %d'%(best, bid))


		self.logger.info('best: %.3f, task_id: %d'%(best, bid))
		self.logger.info(self.rec_json[str(bid)]['params'])
