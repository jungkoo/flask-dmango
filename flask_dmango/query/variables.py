#-*- coding: utf-8 -*-
import json as json_lib
from bson.objectid import ObjectId
import datetime as datetime_lib


def empty_value_none(func):
    def inner(*args, **kwargs):
        if len(args) >=0 and (args[0] is None or "" == args[0]):
            return None
        return func(*args, **kwargs)
    return inner


# 정의된  obj_type 이면 기냥  by pass  한다.
def same_object_by_pass(obj_type):
    def inner(f):
        def warpped_f(*args, **kwargs):
            if isinstance(args[0], obj_type):
                return args[0]
            else:
                return f(*args, **kwargs)
        return warpped_f
    return inner



@empty_value_none
@same_object_by_pass(datetime_lib.date)
def to_date_time(s):
    s = str(s)
    length = len(s)
    year = month = day = hour = minute = sec = 0
    if length < 8:
        raise TypeError('datetime length is short. (>=8, value: ' + s + ')')
    if length >= 4: year = int(s[:4])
    if length >= 6: month = int(s[4:6])
    if length >= 8: day = int(s[6:8])
    if length >= 10: hour = int(s[8:10])
    if length >= 12: minute = int(s[10:12])
    if length >= 14: sec = int(s[12:14])

    if month > 12: raise TypeError('month error. month: ' + str(month) + ' ,datetime:' + s)
    if day > 31: raise TypeError('day error. day: ' + str(day) + ' ,datetime:' + s)
    if hour > 24: raise TypeError('day error. hour: ' + str(hour) + ' ,datetime:' + s)
    if minute > 59: raise TypeError('day error. hour: ' + str(minute) + ' ,datetime:' + s)
    if sec > 59: raise TypeError('sec error. day: ' + str(sec) + ' ,datetime:' + s)

    return datetime_lib.datetime(year, month, day, hour, minute, sec)


def to_json(s, check_type=None):
    if s is None: return None
    try:
        tmp_json = json_lib.loads(s)
        if not check_type or isinstance(tmp_json, check_type):
            return tmp_json
    except ValueError as e:
        raise TypeError('[ERROR] json parse error !!! ==> %s' % (s,))
    raise TypeError('[ERROR] json parse result type error. (value=' + str(s) + ', result_type=' + str(type(tmp_json)) +
                    ', expected_type=' + str(check_type))

@empty_value_none
@same_object_by_pass(list)
def to_list(s):
    if not s.startswith("[") or not s.endswith("]"):  # json 형태의  list 는 아니지만  ,  를 구분자로 하는 값이 존재한다.
        return s.split(",") if ',' in s else [s]
    return to_json(s, list)

@empty_value_none
@same_object_by_pass(dict)
def to_dict(s):
    return to_json(s, dict)

@empty_value_none
@same_object_by_pass(int)
def to_int(s):
    return int(s)

@empty_value_none
@same_object_by_pass(long)
def to_long(s):
    return long(s)

@empty_value_none
@same_object_by_pass(float)
def to_float(s):
    return float(s)

@empty_value_none
@same_object_by_pass(str)
def to_string(s):
    return str(s)


DATA_TYPE_SYNTAX = {'int': to_int, 'long': to_long, 'float': to_float, 'string': to_string, 'text': to_string,
                    'str': to_string, 'json': to_json, 'datetime': to_date_time, 'list': to_list, 'dict': to_dict,
                    'oid': ObjectId, '': to_string}

if __name__ == '__main__':
    pass
