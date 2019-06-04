#!/usr/bin/python
# -*- coding: utf8 -*-
#########################################################################
# File Name: TableCapture.py
# Author: Toka
# mail: fengweitao@sensetime.com
# Created Time: 2019年06月04日 星期二 14时26分20秒
#########################################################################
from __future__ import unicode_literals
import json
import yaml
import re
from beautifultable import BeautifulTable
import codecs


class TableCapture(BeautifulTable):

    @staticmethod
    def _form_row(row, h):
        return [row.get(_, '') for _ in h]

    @staticmethod
    def _get_common_headers(x):
        heads = set()
        for i in x:
            tmp = set(i.keys())
            heads = heads.union(tmp)
        return list(heads)

    @staticmethod
    def fromText(x, dismiss='', *args, **kwargs):
        x = x.split('\n')
        rows = []
        minlen = -1
        for row in x:
            def meaningful(x):
                return re.match(r'[\S\s]*[A-Za-z0-9]', x)
            if meaningful(row) and (dismiss == '' or re.match(dismiss, row) is None):
                rows.append(row)
                if len(row) < minlen or minlen < 0:
                    minlen = len(row)
        ret = TableCapture(*args, **kwargs)
        preind = -1
        if len(rows) == 0:
            return ret
        for i in range(minlen):
            pre = ''
            flag = True
            for row in rows:
                if row[i] != pre and pre != '' or re.match(r'\w', row[i]):
                    flag = False
                    break
                pre = row[i]
            if flag:
                if i - preind > 1:
                    caps = [row[preind+1:i].strip() for row in rows]
                    ret.append_column(caps[0], caps[1:])
                preind = i
        ends = [row[preind+1:].strip() for row in rows]
        if ''.join(ends) != '':
            ret.append_column(ends[0], ends[1:])
        return ret

    @staticmethod
    def fromDict(x, *args, **kwargs):
        ret = TableCapture(*args, **kwargs)

        def check_type(vs):
            for i in range(len(vs)-1):
                assert type(vs[i]) == type(
                    vs[i+1]), 'All columns or rows must be same type'
        if isinstance(x, dict):
            vs = x.values()
            check_type(vs)
            if len(vs):
                if isinstance(vs[0], dict):
                    headers = TableCapture._get_common_headers(vs)
                    ret.column_headers = [''] + headers
                    for k, v in x.items():
                        ret.append_row(
                            [k] + TableCapture._form_row(v, headers))
                else:
                    for k, v in x.items():
                        ret.append_column(k, v)
        elif isinstance(x, list):
            check_type(x)
            if len(x):
                if isinstance(x[0], dict):
                    headers = TableCapture._get_common_headers(x)
                    ret.column_headers = headers
                    for row in x:
                        ret.append_row(TableCapture._form_row(row, headers))
                else:
                    for row in x:
                        ret.append_row(row)
        return ret

    @staticmethod
    def fromString(x, data_type='text', dismiss='', *args, **kwargs):
        assert data_type in [
            'text', 'json', 'yaml'], 'support types are [text, json, yaml], not %s' % data_type
        if data_type == 'text':
            return TableCapture.fromText(x, dismiss=dismiss, *args, **kwargs)
        if data_type == 'json':
            u = json.loads(x)
            return TableCapture.fromDict(u, *args, **kwargs)
        if data_type == 'yaml':
            u = yaml.load(x)
            return TableCapture.fromDict(u, *args, **kwargs)

    @staticmethod
    def fromFile(x, data_type='text', dismiss='', *args, **kwargs):
        assert data_type in [
            'text', 'json', 'yaml'], 'support types are [text, json, yaml], not %s' % data_type
        fd2 = None
        if hasattr(x, 'read'):
            fd = x
        else:
            fd = codecs.open(x, 'r', 'utf-8')
            fd2 = fd
        x = fd.read()
        ret = TableCapture.fromString(
            x, data_type, dismiss=dismiss, *args, **kwargs)
        if fd2 is not None:
            fd2.close()
        return ret

    def toDict(self):
        u = []
        for r in self:
            t = {self.column_headers[j]: r[j]
                 for j in range(self.column_count)}
            u.append(t)
        return u

    def rotate(self):
        ret = TableCapture(max_width=self.max_table_width,
                           default_alignment=self._default_alignment, default_padding=self._default_padding)
        if len(self):
            new_headers = self.column_headers[0:1] + \
                list(map(str, self[self.column_headers[0]]))
            ret.column_headers = new_headers
            for i in range(1, self.column_count):
                ret.append_row(
                    self.column_headers[i:i+1] + list(self[self.column_headers[i]]))
        return ret


# if __name__ == '__main__':
#     # __author__ == '__toka__'
#     t = TableCapture.fromFile('j.jsom', data_type='json')
#     print(t)
#     print(t.toDict())
#     print(t.rotate())
#     txt = str(t)
#     r = TableCapture.fromString(txt)
#     print(r)
#     txt = str(t.rotate())
#     r = TableCapture.fromString(txt)
#     print(r)
#     r = TableCapture.fromFile('te.txt', max_width=640, dismiss='@')
#     print(r)
