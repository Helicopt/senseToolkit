import os
import sys

def initLoader(cur, global_dict, class_name = '__auto__', disable_module = True):
    root = os.path.dirname(os.path.abspath(cur))
    pkg_path = root
    sysPaths = [os.path.abspath(i) for i in sys.path]
    found = False
    while len(pkg_path):
        for i in sysPaths:
            if pkg_path==i:
                cur = os.path.relpath(cur, pkg_path)
                found = True
                break
        if found: break
        parent = os.path.dirname(pkg_path)
        if parent==pkg_path: break
        pkg_path = parent
    if not found:
        pkg_path = root
        while len(pkg_path):
            f = os.path.join(pkg_path, '__init__.py')
            if not os.path.exists(f):
                cur = os.path.relpath(cur, pkg_path)
                found = True
            if found: break
            parent = os.path.dirname(pkg_path)
            if parent==pkg_path: break
            pkg_path = parent

    # if cur[0]=='/':
    #     cur = cur[len(os.getcwd())+1:]
    if cur[-11:]=='__init__.py' or cur[-12:] in ['__init__.pyc', '__init__.pyo', '__init__.pyw']:
        path = os.path.dirname(cur).replace('/', '.')
    else:
        # if cur[-3:]=='.py':
        #     path = cur[:-3].replace('/', '.')
        # elif cur[-4:] in ['.pyc', '.pyo', '.pyw']:
        #     path = cur[:-4].replace('/', '.')
        raise Exception('Please launch initLoader in __init__.py file.')
    for f in os.listdir(root):
        mname = ''
        if os.path.isfile(os.path.join(root,f)) and f[-3:]=='.py' and f!='__init__.py':
            mname = f[:-3]
        elif os.path.isdir(os.path.join(root,f)) and \
        os.path.exists(os.path.join(root, f, '__init__.py')):
            mname = f
        if mname!='':
            try:
                if path!='':
                    __import__('%s.%s'%(path, mname))
                else:
                    __import__('%s'%(mname))
                print('%s.%s'%(path, mname))
            except ValueError:
                raise Exception('module not exists: [%s.%s], package %s'%(path, mname, cur))
            if class_name == '__auto__':
                cn = mname
            else:
                cn = class_name
            if cn is not None and cn in global_dict[mname].__dict__:
                global_dict[mname] = global_dict[mname].__dict__[cn]
            elif disable_module:
                del global_dict[mname]
    del global_dict['initLoader']
