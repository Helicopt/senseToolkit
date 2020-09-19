#!/usr/bin/python
# -*- coding: utf8 -*-
#########################################################################
# File Name: scripts/gridsearch.py
# Author: Toka
# mail: fengweitao@sensetime.com
# Created Time: 2018年07月31日 星期二 22时31分42秒
#########################################################################
from senseTk.magic import *


def run_f(holder, p, tid):
    # holder.llock.acquire()
    # holder.log(str(p))
    # holder.log('running task %d'% tid)
    # holder.llock.release()
    return (p['p1'] - 7)**2 + (p['p2'] - 2)**2 + 5


def eval_f(holder, tid, result):
    res = {
        'dis': result,
        'aaa': result
    }
    # holder.llock.acquire()
    holder.log('evaluating task %d result: %.2f' % (tid, result))
    # holder.llock.release()
    return res


def rec_f(holder, rec):
    return rec['dis']


def mcmp(x, y):
    if x > y:
        return -1
    else:
        return 0


if __name__ == '__main__':
    # __author__ == '__toka__'
    g = gridSearcher()
    p = {'p1': (1, 10, 1), 'p2': (1, 10, 1)}
    # g.set_cmp(mcmp)
    g.set_max_job(2)
    g.set_params(p).set_run(run_f).set_eval(eval_f).set_rec(rec_f).execute()
