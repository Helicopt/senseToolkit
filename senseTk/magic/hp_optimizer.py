import os
import inspect
import pickle
import functools
import threading
import time
import shutil
from .file_lock import CFileLock


class HyperParamHolder:

    pass


class HyperParamOptimizer:

    ext = '.hppt'

    def __init__(self, name, path='/tmp', mode='train', strategy='best'):
        self._name = name
        self._path = path
        if os.path.isdir(self._path):
            self._path = os.path.join(self._path, self._name + self.ext)
        basedir = os.path.dirname(self._path)
        if not os.path.exists(basedir):
            os.makedirs(basedir, exist_ok=True)
        self.lock = CFileLock(self._path)
        self.load()
        self._related_funcs = {}
        self._mode = mode
        self._strategy = strategy
        self._generate_id()

    @staticmethod
    def _build_new_inputs(arg_info, args, kw_args, hp_name, hp):
        new_args = []
        for aname, arg in zip(arg_info.args, args):
            if aname == hp_name:
                new_args.append(hp)
            else:
                new_args.append(arg)
        new_kwargs = {}
        new_kwargs.update(kw_args)
        new_kwargs[hp_name] = hp
        return new_args, new_kwargs

    @staticmethod
    def _check_inputs(arg_info, args, kw_args, hp_name):
        for aname, arg in zip(arg_info.args, args):
            if aname == hp_name:
                if arg == HyperParamHolder:
                    return True
                else:
                    return False
        for k, v in kw_args.items():
            if k == hp_name:
                if v == HyperParamHolder:
                    return True
                else:
                    return False
        return True

    def load(self, path=None):
        if path is not None:
            self._path = path
            self.lock = CFileLock(self._path)
        if os.path.exists(self._path):
            self.lock.lock()
            with open(self._path, 'rb') as fd:
                self._data = pickle.load(fd)
            self.lock.unlock()
        else:
            self._data = {}

    def _generate_id(self):
        self._id = (threading.current_thread().ident << 16) % int(
            1e9+7) + int(time.time() * 10e7) % int(1e9+7)
        self._id %= (1e9+7)

    def _calc_best(self, force=False):
        for fname in self._data.keys():
            if not force and self._data[fname].get('best_hp', None):
                continue
            rec = {}
            for k in self._data[fname]['data'].keys():
                da = self._data[fname]['data'][k]
                for hp_name, hp, score in da:
                    n = int(hp * 1e9)
                    t = rec.get(n, [])
                    t.append(score)
                    rec[n] = t
            best_hp = None
            best_score = None
            for k, v in rec.items():
                v = sum(v) / max(len(v), 1)
                if best_score is None or v > best_score:
                    best_score = v
                    best_hp = k / 1e9
            if best_hp is None:
                raise ValueError('no data for evaluation')
            else:
                self._data[fname]['best_hp'] = best_hp
                self._data[fname]['best_score'] = best_score

    def save(self):
        self.lock.lock()
        if os.path.exists(self._path):
            with open(self._path, 'rb') as fd:
                existed_data = pickle.load(fd)
            for fname in existed_data:
                if fname not in self._data:
                    self._data[fname] = existed_data[fname]
                else:
                    for k in existed_data[fname]['data']:
                        if k not in self._data[fname]['data']:
                            self._data[fname]['data'][k] = existed_data[fname]['data'][k]
        self._calc_best(force=True)
        with open(self._path, 'wb') as fd:
            pickle.dump(self._data, fd)
        self.lock.unlock()

    def optimize(self, hyper_params=None):

        def func_wrapper(old_func):
            if hyper_params is None:
                return old_func
            arg_info = inspect.getfullargspec(old_func)
            fname = old_func.__name__
            hp_name, start, end, delta = hyper_params
            if fname not in self._data:
                self._data[fname] = {'data': {}, 'hp_name': hp_name}
            if self._id not in self._data[fname]['data']:
                self._data[fname]['data'][self._id] = []

            @functools.wraps(old_func)
            def new_func(*args, **kwargs):
                if not self._check_inputs(arg_info, args, kwargs, hp_name):
                    return old_func(*args, **kwargs)
                if self._mode == 'train':
                    hp = start
                    best_out = None
                    best_score = None
                    best_hp = None
                    assert fname in self._related_funcs, 'evaluate function not found'
                    while start <= end and hp <= end or start >= end and hp >= end:
                        new_args, new_kwargs = self._build_new_inputs(
                            arg_info, args, kwargs, hp_name, hp)
                        out = old_func(*new_args, **new_kwargs)
                        score = self._related_funcs[fname](out)
                        if best_score is None or score > best_score:
                            best_score = score
                            best_hp = hp
                            best_out = out
                        self._data[fname]['data'][self._id].append(
                            (hp_name, hp, score))
                        hp += delta
                    self.save()
                if self._strategy == 'best' and self._mode == 'train':
                    return best_out
                else:
                    self._calc_best()
                    hp = self._data[fname]['best_hp']
                    new_args, new_kwargs = self._build_new_inputs(
                        arg_info, args, kwargs, hp_name, hp)
                    out = old_func(*new_args, **new_kwargs)
                    return out
            return new_func
        return func_wrapper

    def evaluate(self, map_to):
        def func_wrapper(old_func):
            if not isinstance(map_to, (list, tuple)):
                map_to_ = [map_to]
            else:
                map_to_ = map_to
            for i in map_to_:
                if inspect.isfunction(i):
                    self._related_funcs[i.__name__] = old_func
                elif isinstance(i, str):
                    self._related_funcs[i] = old_func
                else:
                    raise ValueError('unknown matching target')
            return old_func
        return func_wrapper

    def get_hyper_params(self):
        self._calc_best()
        ret = {}
        for fname in self._data:
            ret[self._data[fname]['hp_name']] = self._data[fname]['best_hp']
        return ret

    def remove(self):
        if os.path.exists(self._path):
            os.remove(self._path)
        try:
            if os.path.exists(self._path+'.lock'):
                os.remove(self._path+'.lock')
        except:
            pass
