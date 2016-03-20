# -*- coding: utf-8 -*-
from collections import namedtuple

from flask_dmango.query.exceptions import NotSupportMethod
from flask_dmango.query.methods import METHOD_FUNCTION_DICT
from flask_dmango.query.variables import DATA_TYPE_SYNTAX


def to_cast(values, type_name=None, convert_list=False):
    """
        드망고에 정의된 타입정보를 이용해  values 를 변환해 준다.
        tip: <필드명>__<메소드명>[]:<type_name>=value & ....
    @param values:  값을 의미한다. 내부적으로 [] 인 값과 단일값을 알아서 체크해 준다.
    @param type_name: 타임명을 의미한다. 드망고의 :<type_name> 을 의미한다.
    @param convert_list: 드망고에서 리스트 타입을 사용자가 강제화 한 경우를 의미한다. []를 강제화 하여 사용한 경우이다.
    예를 들면,  img[]=1_jpg&img[]=2_jpg ... 이때는 1개일때도 강제로 list 의 값으로 자동변환된다.
    @return:
    """
    val = None
    if isinstance(values, list):
        length = len(values)
        if length <= 0:
            return None
        if length > 1:
            val = values
        if length == 1 and convert_list:
            val = values
        if length == 1 and not convert_list:
            val = values[0]
    else:
        val = [values] if convert_list else values

    try:
        if not type_name:
            return val
        return map(lambda v:DATA_TYPE_SYNTAX[type_name](v), val) if isinstance(val, list) else DATA_TYPE_SYNTAX[type_name](val)
    except Exception as e:
        raise TypeError('unknown type name "%s" <%s>' % (type_name,str(e)))


def to_method_value(_field_name, _values, _method_name=None, _sub_map_key=None):
    """
    메소드에 따라 쿼리를 생성한다.
    @param _field_name: 필드명
    @param _values: 값
    @param _method_name: 메소드명을 의미한다.  in , nin, istartswith  같은 값을 의미한다.
    @param _sub_map_key :  '필드명[서브맵키]' 형태로 정의된것으로 dict 로 만들어 져야 할 경우를 의미한다.
    @return:
    """
    if _values is None or _values == '': return None
    mn = _method_name.lower() if _method_name else ''
    if mn in METHOD_FUNCTION_DICT:
        if _sub_map_key:
            return {_field_name: METHOD_FUNCTION_DICT[mn](_sub_map_key, _values)}
        else:
            return METHOD_FUNCTION_DICT[mn](_field_name, _values)
    raise NotSupportMethod(_method_name)


def __min_idx(*args):
    f = filter(lambda x: x >= 0, args)
    return min(f) if f else 0


def __find_sidx(s, find_str, default_val=-1):
    t = s.find(find_str)
    if t < 0: return default_val
    t += len(find_str)
    return t if t > 0 else default_val


def field_name(token=''):
    end_idx = __min_idx(token.find('__'), token.find(':'), token.find('~'), len(token))
    if token == 0: raise TypeError('empty value.')
    if end_idx <= 0: raise TypeError('"field_name" not found. (=' + str(token) + ')')

    # [OK]
    return token[:end_idx]


def field_sub_info(field_name=''): # return (필드명,<서브필드명[|None]>,<타입[list|dict|None]>)
    if field_name.endswith('[]'):
        return field_name[:-2], None, 'list'
    if field_name.find('[') > 0 and field_name.endswith(']'):
        main_key = field_name[:field_name.find('[')]
        sub_key = field_name[field_name.find('[') + 1:-1]
        return main_key, sub_key, 'dict'
    return field_name, None, None



def method_name(token=''):
    start_idx = __find_sidx(token, '__')
    if start_idx < 0: return ''
    end_idx = __min_idx(token.find(':'), token.find('~'), len(token))
    method = token[start_idx:end_idx]
    return '' if method == 'exact' else method


def type_name(token=''):
    start_idx = __find_sidx(token, ':')
    if start_idx<0: return ''
    if token.find('__',start_idx)>=0:
        raise TypeError('[DMANGO-100009] "type" is next "method" unexpected. (=' + str(token) + ')')
    end_idx = __min_idx(token.find('~',start_idx), len(token))
    f = token[start_idx:end_idx]
    return f if len(f) > 0 else None



def nick_name(token=''):
    start_idx = __find_sidx(token, '~')
    if start_idx < 0 : return ''
    if max(token.find('__',start_idx), token.find(':',start_idx)) > 0:
        raise TypeError('[DMANGO-100009] "nickname" is next "method" or "type" unexpected. (=' + str(token) + ')')
    return token[start_idx:]


DmangoFieldInfo = namedtuple('DmangoFieldInfo', ['field_name','sub_field_name','method_name','type_name','sub_type_name','nick_name'])


def to_dmango_field_info(dmango_field_name):
    """
    드망고의 필드명을 정보로 쪼갠다.

    @param dmango_field_name:
    @return:
    """
    _field_name, _sub_field_name, _sub_type_name = field_sub_info(field_name(dmango_field_name))
    _method_name = method_name(dmango_field_name)
    _type_name = type_name(dmango_field_name)
    _nick_name = nick_name(dmango_field_name)
    return DmangoFieldInfo(field_name=_field_name, sub_field_name=_sub_field_name,
                           method_name=_method_name, type_name=_type_name,
                           sub_type_name=_sub_type_name, nick_name=_nick_name)


def to_variable(dmango_field_info, values):
    """
    드망고 필드정보를를 이용한 값을 하나 생성한다.
    @param dmango_field_info: DmangoFieldInfo  타입정보를 의미한다.
    @param values:
    @return: {필드명: 값}  or {필드명 : {메소드: 값...}}
    """
    try:
        df = dmango_field_info
        value = to_cast(values, df.type_name, 'list' == df.sub_type_name)
        return to_method_value(df.field_name, value, df.method_name, df.sub_field_name)
    except TypeError as e:
        raise Exception('[DMANGO-100022] value cast error. (type=%s, values=%s)' % (str(df.type_name), str(values)))
    except Exception as e:
        if not isinstance(dmango_field_info, DmangoFieldInfo):
            raise TypeError('[DMANGO-100021] argument type error. (extected type = "DmangoFieldInfo")')
        if not df.type_name in DATA_TYPE_SYNTAX:
            raise Exception('[DMANGO-100020] unknown "field_type" name. (you=%s, extected="%s")' %
                            (str(df.type_name) , str(DATA_TYPE_SYNTAX.keys()),))
        raise Exception('[DMANGO-100023] maybe crazy variable error. %s' % str(e))




if __name__ == '__main__':
    print ">>>>> to_cast : start "
    print '01', type(to_cast('1234')) == str
    print '02', type(to_cast('1234','int')) == int
    print '03', type(to_cast(['1234'],'int')) == int
    print '04', to_cast(['1234'],'list') == ['1234'] # :list == > [1234]
    print '05', to_cast('1234','list') == ['1234'] # :list == > [1234]
    print '06', to_cast(['1234']) == '1234' # == > 1234
    print '07', to_cast(['1234,5678'],'list') == ['1234','5678'] # :list, 1234,5678 -> ['1234','5678']
    print '08', to_cast(['1234','5678'], 'int', True) == [1234, 5678] # == > [1234,5678]
    print '09', to_cast(['12,34','56,78'], 'list', True) == [['12','34'],['56','78']] # == > [['12','34'],['56','78']]
    print '10', to_cast(['12,34'], 'list', True) == [['12','34']]# == > [['12','34']]
    print '11', to_cast('12,34', 'list') == ['12','34']# == > ['12','34']
    print '12', to_cast([], 'list') == None# == > None
    print '13', to_cast([], 'list', True) == None # == > None
    print '14', to_cast('A', None, True) == ['A'] # == > [A]
    print '15', to_cast(['A'], None, True) == ['A'] # == > [A]
    print '16', to_cast(['123','456'], 'str', True) == ['123','456'] # []:str ==> ['123','456']
    print '17', to_cast(['{"name":"jmc", "age":33}'], 'json', True) == [{u'name':u'jmc', u'age':33}]# []:json ==> [{name:jmc, age:33}]
    print '18', to_cast(['{"name":"jmc", "age":33}'], 'json', False) == {u'name':u'jmc', u'age':33}# []:json ==> {name:jmc, age:33}
    print '19', to_cast(['1234','555'],'int') == [1234, 555]# :int ...
    print ">>>>> to_cast : end "
    print ""

    print ">>>>> to_one_vaue : start "
    print "01", to_method_value("title",'GIL_DONG')
    print "02", to_method_value("title",'GIL_DONG', 'in')
    print "03", to_method_value("user",'GIL_DONG', 'in', 'title')
    print "04", to_method_value("user",['GIL_DONG','HIHI'], 'in', 'title')
    print "05", to_method_value("user",['GIL_DONG','HIHI'], 'like')
    print ">>>>> to_one_value : end "
    print ""

    print ">>>>> to_dmango_field_info : start "
    print "01", to_dmango_field_info("title[sub]:int~tag")
    print "02", to_dmango_field_info("title")
    print "03", to_dmango_field_info("title:list")
    print "04", to_variable(to_dmango_field_info("title:list"), 'jmc')
    print ">>>>> to_dmango_field_info : end "
    print "end"
