#!/usr/bin/python
# -*- coding: utf8 -*-
#########################################################################
# File Name: functions/__init__.py
# Author: Toka
# mail: fengweitao@sensetime.com
# Created Time: 2018年07月27日 星期五 15时32分36秒
#########################################################################

import cv2

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