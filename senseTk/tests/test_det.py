from pytest import approx
from senseTk.common import Det, TrackSet
from tempfile import NamedTemporaryFile

def test_dets():
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
    a.cx -= 150
    assert(a._trim(sz = (1920, 1080), toInt = False).x1==approx(0))
    assert(a._trim(sz = (1920, 1080), toInt = False).cx==approx((101.3+1+67.2-150)/2.))
    assert(a._trim(sz = (1920, 1080), toInt = True).cx==approx(int((101.3+1+67.2-150)/2)))

def test_trackset():
    with NamedTemporaryFile(delete=False, mode='w') as ntf:
        ntf.write(
            '1,0,10,10,20,20\n'
            '2,0,10,10,20,20\n'
            '3,0,10,10,20,20\n'
            '4,0,10,10,20,20\n'
            '1,2,110,10,20,20\n'
            '2,2,110,10,20,20\n'
            '3,2,110,10,20,20\n'
            '4,2,110,10,20,201\n'
        )
    try:
        ts = TrackSet(ntf.name)
        assert(False)
    except Exception as e:
        if type(e)!=AssertionError:
            assert(e.args[0]=='Unknown Format')
        else:
            raise e
    ts = ts = TrackSet(ntf.name, formatter='fr.i,id.i,x1,y1,w,h')
    for i in range(1,5):
        assert(len(ts[i])==2)
        assert(ts.fr_count(i)==2)
    assert(len(ts[0])==0)
    assert(len(ts[5])==0)
    assert(ts.fr_count()==4)
    assert(ts.id_count()==2)
    assert(ts.id_count(1)==0)
    assert(ts.id_count(2)==4)
    assert(ts.count()==8)
    ts.append_data(Det(5,5,5,5, fr=1, uid=3))
    assert(ts.fr_count()==4)
    assert(ts.id_count()==3)
    assert(ts.count()==9)

    tsa = ts(1)
    assert(tsa is None)
    tsa = ts(2)
    tsa2 = ts(2)
    assert(id(tsa)==id(tsa2))
    assert(tsa.count()==4 and tsa.fr_count(4)==1 and tsa[4][0].area()==4020)
    ts.delete(tsa[4][0])
    ts.delete(ts[4][0])
    assert(ts.fr_count()==3)
    assert(ts.id_count()==3)
    assert(ts.count()==7)
    ts[2:4] = tsa[2:4]
    assert(ts.fr_count()==3)
    assert(ts.id_count()==3)
    assert(ts.count()==5)
    tsa[2:] = None
    assert(tsa.fr_count()==1)
    assert(tsa.id_count()==1)
    assert(tsa.count()==1)
    tsa[:2] = None
    assert(tsa.fr_count()==0)
    assert(tsa.id_count()==0)
    assert(tsa.count()==0)
    with NamedTemporaryFile(delete=False, mode='w') as ntf:
        ntf.write(
            '1,0,10,10,20,20\n'
            '2,0,10,10,20,20\n'
            '3,0,10,10,20,20\n'
            '4,0,10,10,20,20\n'
            '1,2,110,10,20,20\n'
            '2,2,110,10,20,20\n'
            '3,2,110,10,20,20\n'
            '4,2,110,10,20,201\n'
            '2,3,110,10,20,20\n'
            '3,3,110,10,20,20\n'
            '4,3,110,10,20,201\n'
        )
    ts = TrackSet(ntf.name, formatter='fr.i,id.i,x1,y1,w,h')
    a = ts(0)
    b = ts(2)
    c = ts(3)
    tsa = a + b
    assert(tsa.fr_count()==4)
    assert(tsa.id_count()==2)
    assert(tsa.count()==8)

    assert(c.fr_count()==3)
    assert(c.id_count()==1)
    assert(c.count()==3)

    tsb = b + c

    assert(b.fr_count()==4)
    assert(b.id_count()==1)
    assert(b.count()==4)

    assert(tsb.fr_count()==4)
    assert(tsb.id_count()==2)
    assert(tsb.count()==7)

    iddr = id(tsb)

    tsb += a

    assert(tsb.fr_count()==4)
    assert(tsb.id_count()==3)
    assert(tsb.count()==11)
    assert(id(tsb)==iddr)

    assert(b.fr_count()==4)
    assert(b.id_count()==1)
    assert(b.count()==4)

