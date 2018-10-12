import os

def initLoader(cur, global_dict, class_name = '__auto__', disable_module = True):
    root = os.path.dirname(os.path.abspath(cur))
    if cur[0]=='/':
        cur = cur[len(os.getcwd())+1:]
    if cur[-11:]=='__init__.py' or cur[-12:]=='__init__.pyc':
        path = os.path.dirname(cur).replace('/', '.')
    else:
        if cur[-3:]=='.py':
            path = cur[:-3].replace('/', '.')
        elif cur[-4:]=='.pyc':
            path = cur[:-4].replace('/', '.')
    for f in os.listdir(root):
        mname = ''
        if os.path.isfile(os.path.join(root,f)) and f[-3:]=='.py' and f!='__init__.py':
            mname = f[:-3]
        elif os.path.isdir(os.path.join(root,f)) and \
        os.path.exists(os.path.join(root, f, '__init__.py')):
            mname = f
        if mname!='':
            try:
                __import__('%s.%s'%(path, mname))
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
