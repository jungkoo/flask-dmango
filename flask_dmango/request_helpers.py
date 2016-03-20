# -*- coding: utf-8 -*-
from UserDict import UserDict
from abc import ABCMeta, abstractmethod
from bson import ObjectId
from flask import request
from flask_pymongo import DESCENDING, ASCENDING
from flask_dmango.mongodb_helpers import DmangoQueryBuilder, dmango_query


class AbstractRequestDmango(UserDict, dict):

    def __init__(self, req):
        assert req is request
        UserDict.__init__(self)
        self.args = req.args
        self.is_parse = False

    @abstractmethod
    def parse(self, args):
        raise Exception('parse logic override ')

    def lazy_parse(self):
        """
        요청이 없을때는 파싱하는 문제를 해결하기위해 파싱은 최대한 미룬다.
        @param args:
        @param kwargs:
        @return:
        """
        if not self.is_parse:
            self.parse(self.args)


    @property
    def sort(self):
        self.lazy_parse()
        return self.get('sort', None)

    @sort.setter
    def sort(self, value):
        self.__setitem__('sort', value)

    @property
    def page_num(self):
        self.lazy_parse()
        return self.get('page_num', None)

    @page_num.setter
    def page_num(self, value):
        self.__setitem__('page_num', value)

    @property
    def page_size(self):
        self.lazy_parse()
        return self.get('page_size', None)

    @page_size.setter
    def page_size(self, values):
        self.__setitem__('page_size', values)

    @property
    def start_idx(self):
        self.lazy_parse()
        return self.get('start_idx', None)

    @start_idx.setter
    def start_idx(self, values):
        self.__setitem__('start_idx', values)

    @property
    def end_idx(self):
        self.lazy_parse()
        return self.get('end_idx', None)

    @end_idx.setter
    def end_idx(self, values):
        self.__setitem__('end_idx', values)

    @property
    def match(self):
        self.lazy_parse()
        return self.get('match', None)

    @match.setter
    def match(self, values):
        self.__setitem__('match', values)

    @property
    def unwind(self):
        self.lazy_parse()
        return self.get('unwind', None)

    @unwind.setter
    def unwind(self, values):
        self.__setitem__('unwind', values)

    @property
    def group(self):
        self.lazy_parse()
        return self.get('group', None)

    @group.setter
    def group(self, values):
        self.__setitem__('group', values)

    @property
    def fields(self):
        self.lazy_parse()
        return self.get('fields', None)

    @fields.setter
    def fields(self, values):
        self.__setitem__('fields', values)

    @property
    def id(self):
        self.lazy_parse()
        return self.get('id', None)

    @id.setter
    def id(self, value):
        self.__setitem__('id', value)

    @property
    def options(self):
        self.lazy_parse()
        return self.get('options', None)

    @options.setter
    def options(self, value):
        self.__setitem__('options', value)


class RequestDmango(AbstractRequestDmango):
    def parse(self, args):
        self.update(parse_match(args))
        self.update(parse_sort(args))
        self.update(parse_offset(args))
        self.update(parse_group(args))
        self.update(parse_id(args))
        self.update(parse_options(args))
        self.update(parse_fields(args))


def split_generator(values):
    for line in values if isinstance(values, (tuple,list)) else tuple(values):
        for val in line.split(','):
            yield val


def parse_offset(args):
    _page_num = int(args.get('_page_num', 1))
    _page_size = int(args.get('_page_size', 20))
    _start_idx = int(args.get('_start_idx', (_page_num-1)*_page_size))
    _end_idx = int(args.get('_end_idx', (_page_num*_page_size)-1))
    return {'page_num': _page_num, 'page_size':  _page_size, 'start_idx': _start_idx, 'end_idx': _end_idx}


def parse_sort(args):
    _sort = []
    for sort_value in args.getlist('_sort'):
        t = sort_value.split('__')
        if len(t) == 2 and t[1] in ('desc','DESC'):
            _sort.append((t[0], DESCENDING))
        elif len(t[0]) > 0:
            _sort.append((t[0], ASCENDING))
    return {'sort': _sort}

find_field_end_idx_fn = lambda text, delis: min(text.find(d) if text.find(d) > 0 else len(text) for d in delis)

def parse_match(args):
    _query = DmangoQueryBuilder()
    exclude_fields = {k: True for k in split_generator(args.getlist('_exclude_query_fields'))}
    for dmango_fn in filter(lambda x: not x.startswith("_"), args):
        field_end_idx = find_field_end_idx_fn(dmango_fn,  ('__', ':', '~'))
        field_name = dmango_fn[:field_end_idx]
        if exclude_fields.has_key(field_name):
            continue # _exclude_query_fields 라면 제외
        _query.query(dmango_fn, args.getlist(dmango_fn))

    return {'match': _query()}


def parse_group(args):
    return {'unwind': split_generator(args.getlist('_unwind')), 'group': args.getlist('_group')}


def parse_id(args):
    return {'id': ObjectId(args.get('_id')) if args.get('_id') else None}


def parse_fields(args):
    _fields = {k: True for k in filter(lambda x: x and len(x) > 0, split_generator(args.getlist('_fields')))}
    return {'fields': _fields}


def parse_options(args):
    _options = {}
    for val in split_generator(args.getlist('_options')):
        t = val.split(":")
        if len(t)==2:
            _options[str(t[0])] = str(t[1].strip())
    return {'options': _options}



if __name__ == '__main__':
    pass