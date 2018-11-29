#!/usr/bin/python
# -*- coding: utf8 -*-
#########################################################################
# File Name: magic/__init__.py
# Author: Toka
# mail: fengweitao@sensetime.com
# Created Time: 2018年07月27日 星期五 12时31分26秒
#########################################################################

try:
    from .ImageGallery import IMGallery, requireQA
except:
    pass
from .FileAgent import *
from .GridSearch import gridSearcher, OrderedDict
from .gtSearcher import gtSearcher, default_gt_search_config, make_gt_config
from .pyAutoLoader import initLoader
