#-*- coding: utf-8 -*-


class DmangoException(Exception):
    def __init__(self, message):
        self._message = message

    def _get_message(self):
        return self._message

    def _set_message(self, message):
        self._message = message

    message = property(_get_message, _set_message)


class NotSupportMethod(DmangoException):
    def __init__(self, method):
        self.method = method

    def __str__(self):
        return '"%s" is not a valid method name' % (str(self.method), )


class DmangoValueException(DmangoException):
    """
     value 를 관련 문제를 의미한다.
     예를 들어 'a' 를  int 로 변경하려고 했을경우라거나... 값이 허용되는게 아니라거나.
    """
    def __init__(self, value_name):
        self._value_name = value_name

    def __str__(self):
        return '[DMANGO-100002] value Error. (value name="%s")' % (self._value_name,)



class DmangoParseException(DmangoException):
    def __init__(self, errmsg='parse error'):
        self.errmsg = errmsg

    def __str__(self):
        return "[DMANGO-100003] " + self.errmsg
