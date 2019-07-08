import os
import sys

def initLoader(cur, module_dict, class_name = '__auto__'):
    curs = []
    if isinstance(cur, str):
        b, ext = os.path.splitext(os.path.basename(cur))
        if os.path.isfile(cur) and b!='__init__':
            curs = [cur]
        elif os.path.isdir(cur) or os.path.isfile(cur) and b=='__init__':
            if os.path.isfile(cur) and b=='__init__':
                cur = os.path.dirname(cur)
            combine = lambda x: os.path.join(cur, x)
            curs = map(combine, os.listdir(cur))
    else:
        curs = cur
    curs = list(map(os.path.abspath, curs))

    olds = sys.path
    sysPaths = [os.path.abspath(i) for i in olds]

    cache = {}
    for c in curs:
        b, ext = os.path.splitext(os.path.basename(c))
        if (ext in ['.py', '.pyo', '.pyw', '.pyc'] or ext=='' and os.path.isdir(c)) and len(b)>0 and b[0]!='_':
            d = os.path.abspath(os.path.dirname(c))
            r = cache.get(d, False)
            if r==False:
                pkg_path = d
                r = None
                while len(pkg_path):
                    for i in sysPaths:
                        if pkg_path==i:
                            r = os.path.relpath(d, pkg_path)
                            break
                    if r is not None: break
                    parent = os.path.dirname(pkg_path)
                    if parent==pkg_path: break
                    pkg_path = parent
                cache[d] = r
            if r is not None:
                if r=='.':
                    mname = b
                else:
                    mname = r.replace('/', '.') + '.' + b
            else:
                sys.path = [d] + olds
                mname = b
            if class_name is None:
                m = __import__(mname, fromlist=[''])
            elif class_name=='__auto__':
                m = getattr(__import__(mname, fromlist=['']), b)
            else:
                m = getattr(__import__(mname, fromlist=['']), class_name)
            module_dict[b] = m

            sys.path = olds

    return module_dict
