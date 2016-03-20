#-*- coding: utf-8 -*-
from functools import wraps
from flask import current_app, request
from bson.json_util import dumps
import time

current_milli_time = lambda: int(round(time.time() * 1000))

def dmango_api_template(api_name, indent=None):
    """
    dict형태를 json형태로 리턴하는 템플릿
    @param api_name: api명
    @return:
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            start_time = current_milli_time()
            seed_result = {'api_name': api_name, 'msg': '성공', 'status': 200}
            try:
                ctx = f(*args, **kwargs) or dict()  ## flask.route 실행
                seed_result.update(**ctx)
            except Exception as e:
                seed_result['msg'] = '실패 (%s)' % (e,)
                seed_result['status'] = 404
                ctx = {}
            seed_result['time(ms)'] = current_milli_time() - start_time

            _indent = indent
            if hasattr(request, 'dmango') and not _indent:
                _indent = 2 if request.dmango.options.get('indent') in ('true', 'True', 'TRUE', 'YES', '1', 'Y') else None

            return current_app.response_class(dumps(seed_result, indent=_indent, ensure_ascii=False),
                                              mimetype='text/json;charset=UTF-8')
        return decorated_function
    return decorator