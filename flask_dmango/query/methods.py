#-*- coding: utf-8 -*-
"""
    method 에 대한 처리를 한다.
    mongodb 의 오퍼레이션에 대한 처리를 위한 펑션이 모인곳으로 알면된다.
"""
import re as rex

from flask_dmango.query.exceptions import DmangoValueException


def __default_rex_search(f, v, func):
    if isinstance(v, list):
        return {f: {'$in': [func(_v) for _v in v]}}
    if isinstance(v, unicode) or isinstance(v, str):
        return {f: func(v)}
    raise TypeError("NOT Support Type.")


def like(f, v):
    return __default_rex_search(f, v, lambda _v: rex.compile(rex.escape(unicode(_v))))


def ignore_case_like(f, v):
    return __default_rex_search(f, v, lambda _v: rex.compile(rex.escape(unicode(_v)), flags=rex.IGNORECASE))


def startswith(f, v):
    return __default_rex_search(f, v, lambda _v: rex.compile('^' + rex.escape(unicode(_v))))


def ignore_case_startswith(f, v):
    return __default_rex_search(f, v, lambda _v: rex.compile('^' + rex.escape(unicode(_v)), flags=rex.IGNORECASE))


def endswith(f, v):
    return __default_rex_search(f, v, lambda _v: rex.compile(rex.escape(unicode(_v)) + '$'))


def ignore_case_endswith(f, v):
    return __default_rex_search(f, v, lambda _v: rex.compile(rex.escape(unicode(_v)) + '$', flags=rex.IGNORECASE))


def exact(f, v):
    return {f: v}


def gt(f, v):
    return {f: {'$gt': v}}


def gte(f, v):
    return {f: {'$gte': v}}


def lt(f, v):
    return {f: {'$lt': v}}


def lte(f, v):
    return {f: {'$lte': v}}


def not_equals(f, v):
    return {f: {'$ne': v}}


def contains(f, v):
    if not isinstance(v, list):
        return {f: {'$in': [v]}}
    return {f: {'$in': v}}


def not_contains(f, v):
    if not isinstance(v, list):
        return {f: {'$nin': [v]}}
    return {f: {'$nin': v}}


def between(f, v):
    if not isinstance(v, list) and not isinstance(v, tuple):
        raise TypeError('$betwwen method is support only list type. (error = "%s")' % (str(type(v)),))
    if len(v) != 2:
        raise DmangoValueException('$betwwen method is two value expected, but size = %d' % (len(v),))
    start_val = v[0] if v[0] < v[1] else v[1]
    end_val = v[0] if v[0] > v[1] else v[1]
    return {f: {'$gte': start_val, '$lte': end_val}}


METHOD_FUNCTION_DICT = {'like': like, 'ilike': ignore_case_like, 'gt': gt, 'lt': lt, 'gte': gte, 'lte': lte,
                        'in': contains, 'nin': not_contains, 'ne': not_equals, '': exact, 'startswith': startswith,
                        'endswith': endswith, 'istartswith': ignore_case_startswith, 'iendswith': ignore_case_endswith,
                        'between': between
                        }

if __name__ == '__main__':
    pass