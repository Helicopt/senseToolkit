import os
import inspect
import pickle
import functools
import threading
import time
import shutil
import numpy as np
from .file_lock import CFileLock


class HyperParamHolder:

    def __init__(self, name=None, hp_type=None, options=None):
        self._name = name
        self._type = hp_type
        self._options = self.build_options(hp_type, options)

    @staticmethod
    def build_options(_type, _options):
        if _type == 'range':
            start, end, delta = _options
            ptr = start
            assert start <= end and delta > 0 or start >= end and delta < 0
            ret = []
            while start <= end and ptr <= end or start >= end and ptr >= end:
                ret.append(ptr)
                ptr += delta
            return ret
        if _type == 'options':
            assert len(_options)
            return list(_options)

    def sample(self, num):
        inds = np.random.choice(np.arange(len(self._options)), num)
        ret = []
        for i in range(num):
            i = int(inds[i])
            ret.append(self._options[i])
        return ret

    def __len__(self):
        return len(self._options)


class HyperParamGroup:

    def __init__(self, *args, sample_num=None):
        self._hps = args
        self._sample_num = sample_num
        for hp in self._hps:
            assert isinstance(hp, HyperParamHolder)

    def sample(self, num=None, replace=False):
        if num is None:
            num = self._sample_num
        size = []
        total = 1
        for one in self._hps:
            size.append(len(one))
            total *= len(one)
        assert num <= total
        if total > num * 10:
            inds = []
            cnt = 0
            while cnt < num:
                i = np.random.randint(0, total)
                if not replace and i in inds:
                    continue
                else:
                    inds.append(i)
                    cnt += 1
        else:
            inds = np.random.choice(
                np.arange(total, dtype=np.int), num, replace=replace)
        ret = []
        for i in inds:
            i = int(i)
            item = {}
            for one, s in zip(self._hps, size):
                k = i % s
                i //= s
                item[one._name] = one._options[k]
            ret.append(item)
        return ret

    def to_dict(self):
        ret = {}
        for one in self._hps:
            ret[one._name] = {
                'type': one._type,
                'options': one._options,
            }
        return ret

    def _from_dict(self, dict_):
        hps = []
        for k, v in dict_.items():
            tmp = HyperParamHolder(k)
            tmp._type = v['type']
            tmp._options = v['options']
            hps.append(tmp)
        self._hps = hps
        return self

    @staticmethod
    def from_dict(dict_):
        tmp = HyperParamGroup()
        return tmp._from_dict(dict_)

    def __len__(self):
        return len(self._hps)

    def __iter__(self):
        return iter(self._hps)

    def __getitem__(self, x):
        if isinstance(x, (int, slice)):
            return self._hps[x]
        elif isinstance(x, str):
            for i in self._hps:
                if i._name == x:
                    return i
            raise KeyError

    def __setitem__(self, x, y):
        if isinstance(x, (int, slice)):
            self._hps[x] = y
        elif isinstance(x, str):
            for k, i in enumerate(self._hps):
                if i._name == x:
                    self._hps[k] = y
                    return
            raise KeyError

    def __contains__(self, x):
        for i in self._hps:
            if i._name == x:
                return True
        return False

    def names(self):
        return (i._name for i in self._hps)


class HyperParamOptimizer:

    ext = '.hppt'

    def __init__(self, name, path='/tmp', mode='train', strategy='best', sample_num=3):
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
        self._sample_num = sample_num
        self._mode = mode
        self._strategy = strategy
        self._generate_id()

    @staticmethod
    def _build_new_inputs(arg_info, args, kw_args, hp):
        new_args = []
        for aname, arg in zip(arg_info.args, args):
            if aname in hp:
                new_args.append(hp[aname])
                del hp[aname]
            else:
                new_args.append(arg)
        new_kwargs = {}
        new_kwargs.update(kw_args)
        new_kwargs.update(hp)
        return new_args, new_kwargs

    @staticmethod
    def _check_inputs(arg_info, args, kw_args, hps):
        hpnames = hps.names()
        for aname, arg in zip(arg_info.args, args):
            if aname in hps:
                if arg == HyperParamHolder:
                    return True
                else:
                    return False
        for k, v in kw_args.items():
            if k in hps:
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
        self._id = int(threading.current_thread().ident << 16) % int(
            1e9+7) + int(time.time() * 10e7) % int(1e9+7)
        self._id %= (1e9+7)

    def _calc_best(self, force=False):

        def convert(names, values):
            ret = []
            for i in names:
                if isinstance(values[i], (int, float)):
                    ret.append(int(values[i] * 1e6))
                else:
                    ret.append(values[i])
            return tuple(ret)

        def inverse(names, values):
            ret = []
            for name, value in zip(names, values):
                if isinstance(value, int):
                    value = value / 1e6
                ret.append((name, value))
            return ret
        for fname in self._data.keys():
            if not force and self._data[fname].get('best', None):
                continue
            rec = {}
            hp_names = list(self._data[fname]['hp'].keys())
            for k in self._data[fname]['data'].keys():
                da = self._data[fname]['data'][k]
                for hp, score in da:
                    n = convert(hp_names, hp)
                    t = rec.get(n, [])
                    t.append(score)
                    rec[n] = t
            best_hp = None
            best_score = None
            for k, v in rec.items():
                v = sum(v) / max(len(v), 1)
                if best_score is None or v > best_score:
                    best_score = v
                    best_hp = inverse(hp_names, k)
            if best_hp is None:
                raise ValueError('no data for evaluation')
            else:
                self._data[fname]['best'] = best_hp
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

    def optimize(self, hyper_params=None, static=True):

        def func_wrapper(old_func):
            if hyper_params is None:
                return old_func
            arg_info = inspect.getfullargspec(old_func)
            fname = old_func.__name__
            if fname not in self._data:
                self._data[fname] = {'data': {}, 'hp': hyper_params.to_dict()}
            if self._id not in self._data[fname]['data']:
                self._data[fname]['data'][self._id] = []

            @functools.wraps(old_func)
            def new_func(*args, **kwargs):
                ctx = args[0] if len(args) else None
                if not self._check_inputs(arg_info, args, kwargs, hyper_params):
                    return old_func(*args, **kwargs)
                if self._mode == 'train':
                    best_out = None
                    best_score = None
                    best_hp = None
                    assert fname in self._related_funcs, 'evaluate function not found'
                    # while start <= end and hp <= end or start >= end and hp >= end:
                    #     new_args, new_kwargs = self._build_new_inputs(
                    #         arg_info, args, kwargs, hp_name, hp)
                    #     out = old_func(*new_args, **new_kwargs)
                    #     if static:
                    #         score = self._related_funcs[fname](out)
                    #     else:
                    #         score = self._related_funcs[fname](ctx, out)
                    #     if best_score is None or score > best_score:
                    #         best_score = score
                    #         best_hp = hp
                    #         best_out = out
                    #     self._data[fname]['data'][self._id].append(
                    #         (hp_name, hp, score))
                    #     hp += delta
                    # self.save()
                    sample_num = hyper_params._sample_num if hyper_params._sample_num is not None else self._sample_num
                    for item in hyper_params.sample(sample_num):
                        new_args, new_kwargs = self._build_new_inputs(
                            arg_info, args, kwargs, item)
                        out = old_func(*new_args, **new_kwargs)
                        if static:
                            score = self._related_funcs[fname](out)
                        else:
                            score = self._related_funcs[fname](ctx, out)
                        if best_score is None or score > best_score:
                            best_score = score
                            best_hp = item
                            best_out = out
                        self._data[fname]['data'][self._id].append(
                            (item, score))
                    # self.save()

                if self._strategy == 'best' and self._mode == 'train':
                    return best_out
                else:
                    self._calc_best()
                    hp = dict(self._data[fname]['best'])
                    new_args, new_kwargs = self._build_new_inputs(
                        arg_info, args, kwargs, hp)
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
            for hp_name, best_hp in self._data[fname]['best']:
                ret[hp_name] = best_hp
        return ret

    def remove(self):
        if os.path.exists(self._path):
            os.remove(self._path)
        try:
            if os.path.exists(self._path+'.lock'):
                os.remove(self._path+'.lock')
        except:
            pass
