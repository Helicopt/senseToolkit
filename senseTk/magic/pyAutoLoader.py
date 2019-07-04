import os
import sys

def initLoader(cur, module_dict, class_name = '__auto__'):
    curs = []
    if isinstance(cur, str):
        if os.path.isdir(cur):
            combine = lambda x: os.path.join(cur, x)
            curs = map(combine, os.listdir(cur))
        else:
            curs = [cur]
    else:
        curs = cur
    curs = list(map(os.path.abspath, curs))
    dirs = set()
    for c in curs:
        d = os.path.abspath(os.path.dirname(c))
        dirs.add(d)

    olds = sys.path
    sys.path = list(dirs) + olds

    for c in curs:
        b, ext = os.path.splitext(os.path.basename(c))
        if ext in ['.py', '.pyo', '.pyw', '.pyc'] and len(b)>0 and b[0]!='_':
            if class_name is None:
                m = __import__(b)
            elif class_name=='__auto__':
                m = getattr(__import__(b), b)
            else:
                m = getattr(__import__(b), class_name)
            module_dict[b] = m

    sys.path = olds

    return module_dict
