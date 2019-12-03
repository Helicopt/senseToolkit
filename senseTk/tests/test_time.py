from pytest import approx
from senseTk.common import Det, TrackSet
import senseTk.extension.functional as F
try:
    import senseTk.extension.boost_functional as bF
    NobF = False
except ImportError as e:
    NobF = True
import time

def test_time1():
    a = Det(101.3, 413.5, 67.2, 201.1)
    assert(a.cx==approx(101.3+67.2/2))
    assert(a.cy==approx(413.5+201.1/2))
    assert(a.x1==approx(101.3))
    assert(a.y1==approx(413.5))
    assert(a.w==approx(67.2))
    assert(a.h==approx(201.1))
    assert(a.x2==approx(101.3+67.2))
    assert(a.y2==approx(413.5+201.1))
    assert(a.area()==approx(67.2*201.1))
    a.cx += 1
    assert(a.x1==approx(101.3+1))
    assert(a.x2==approx(101.3+67.2+1))
    a.y2 += 2
    assert(a.y1==approx(413.5))
    assert(a.cy==approx(413.5+201.1/2+1))
    b = Det(94.5, 510.1, 70.9, 203.7)
    assert(a.intersection(b)==approx((94.5+70.9 - 101.3 - 1)*(413.5+201.1+2 - 510.1)))
    assert(a.iou(b)==\
        approx(a.intersection(b)/(67.2*203.1 + 70.9*203.7 - a.intersection(b)))
    )
    c = 0.
    be = time.time()
    a_ = [a] * 5000000
    b_ = [b] * 5000000
    for i in range(5000000):
        c+=a_[i].iou(b_[i])
    en = time.time()
    t1 = en - be
    # print(t1)
    # assert(t1 < 2)

    c = 0.
    be = time.time()
    for i in range(500000):
        a._trim(sz=(150, 150))
    en = time.time()
    t2 = en - be
    # print(t2)
    # assert(t2 < 1)


def test_time2():
    if not NobF:

        c = 0.
        be = time.time()
        _a = bF.cDet(a.x1, a.y1, a.w, a.h)
        _b = bF.cDet(b.x1, b.y1, b.w, b.h)
        a_ = [_a] * 5000000
        b_ = [_b] * 5000000
        for i in range(5000000):
            c+=a_[i].iou(b_[i])
        en = time.time()
        t1_1 = en - be
        # print(t1_1)
        # assert(t1_1 < 1.5)

        c = 0.
        be = time.time()
        _a = bF.cDet(a.x1, a.y1, a.w, a.h)
        _b = bF.cDet(b.x1, b.y1, b.w, b.h)
        a_ = [_a] * (5000000)
        b_ = [_b] * (5000000)
        ret = bF.c_iou_batch(a_, b_)
        # ret = F.c_iou_batch(a_, b_)
        for i in ret:
            c+=i
        en = time.time()
        t1_2 = en - be
        # print(t1_2)
        # assert(t1_2 < 1)

    