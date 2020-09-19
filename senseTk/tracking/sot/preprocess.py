#!/usr/bin/python
# -*- coding: utf8 -*-
#########################################################################
# File Name: senseTk/tracking/sot/preprocess.py
# Author: Toka
# mail: fengweitao@sensetime.com
# Created Time: 2018年08月02日 星期四 19时22分29秒
#########################################################################
import numpy as np
import cv2
import math
import random
import os
import sys

__all__ = ["siaCrop"]


def get_crop_e(img, bbox, size_z=127, context_amount=0.5):
    x1, y1, x2, y2 = [float(x) for x in [bbox.x1, bbox.y1, bbox.x2, bbox.y2]]
    cx, cy, w, h = (x1+x2)/2, (y1+y2)/2, x2-x1, y2-y1

    wc_z = w + context_amount*(w+h)
    hc_z = h + context_amount*(w+h)
    s_z = math.sqrt(wc_z * hc_z)
    scale_z = size_z / s_z

    nw = w * scale_z
    nh = h * scale_z

    im_crop_z = get_subwindow(img, [cy, cx], [size_z, size_z], [
                              round(s_z), round(s_z)])

    return im_crop_z, scale_z, (size_z-1 >> 1, size_z-1 >> 1, nh, nw)


def get_crop_i(img, bbox, size_z=127, size_x=255, context_amount=0.5):
    x1, y1, x2, y2 = [float(x) for x in [bbox.x1, bbox.y1, bbox.x2, bbox.y2]]
    cx, cy, w, h = (x1+x2)/2, (y1+y2)/2, x2-x1, y2-y1

    wc_z = w + context_amount*(w+h)
    hc_z = h + context_amount*(w+h)
    s_z = math.sqrt(wc_z * hc_z)
    scale_z = size_z / s_z

    d_search = (size_x-size_z) / 2.
    pad = d_search / scale_z
    s_x = s_z + 2 * pad
    scale_x = size_x / s_x

    nw = w * scale_x
    nh = h * scale_x

    im_crop_x = get_subwindow(img, [cy, cx], [size_x, size_x], [
                              round(s_x), round(s_x)])

    return im_crop_x, scale_x, (size_x-1 >> 1, size_x-1 >> 1, nh, nw)


def mean(img):
    avg_color_per_row = np.average(img, axis=0)
    return np.average(avg_color_per_row, axis=0).astype(np.uint8)


def get_subwindow(img, pos, model_sz, original_sz):
    means = mean(img)

    sz = original_sz
    sz = [int(x) for x in sz]
    im_sz = img.shape[0], img.shape[1]

    c = [0, 0]
    c[0] = (sz[0]+1) // 2
    c[1] = (sz[1]+1) // 2

    cxmin = int(round(pos[0] - c[0]))
    cxmax = cxmin + sz[0] - 1
    cymin = int(round(pos[1] - c[1]))
    cymax = cymin + sz[1] - 1

    im = np.zeros((cxmax-cxmin+1, cymax-cymin+1, 3), np.uint8)
    im[:, :] = means

    x1 = max(cxmin, 0)
    y1 = max(cymin, 0)
    x2 = min(cxmax, im_sz[0])
    y2 = min(cymax, im_sz[1])

    x1, y1, x2, y2 = [int(x) for x in [x1, y1, x2, y2]]

    # im[y1-cymin:y2-cymin, x1-cxmin:x2-cxmin] = img[y1:y2, x1:x2]
    im[x1-cxmin:x2-cxmin, y1-cymin:y2-cymin] = img[x1:x2, y1:y2]

    im = cv2.resize(im, tuple(model_sz))

    im_np = im - means

    #im_np = acquireAugment(im_np, model_sz)

    return im, im_np


def siaCrop(im, dt, size_z=127, size_x=511, tag='x', ctx=0.5):
    if tag == 'z':
        return get_crop_e(im, dt, size_z=size_z, context_amount=ctx)
    elif tag == 'x':
        return get_crop_i(im, dt, size_z=size_z, size_x=size_x, context_amount=ctx)
    return None
