#-*- coding: utf-8 -*-
from functools import wraps
from flask import request, render_template_string, current_app

__templated_function_map = {}


def register(name):
    """flask에서 템플릿을 등록할때 사용한다.
    등록된 템플릿을 사용하는것은 @templated 이나 @after 를 사용한다.

    사용예제::

        @register('json')
        def json_template(result, count):
            rv = {'result': result, 'count': count}
            return json.dumps(my_json, ensure_ascii=False)

    @param name: 템플릿이름
    @return:
    """
    def decorator(f):
        __templated_function_map[name] = f
        print ' * View Decorators Register : name=%s, function=%s' % (name , str(f))
        return f
    return decorator


def templated(name=None, begin=None, end=None, exception=None):
    """register에서 등록한 것을 사용할때 이용한다.
    주의할 사항은, dict형태의 파라미터를 받아 string 결과를 만드는 함수가 등록되어 있어야 한다.

        사용예제:
            @app.route('/find')
            @templated('json')
            def find():
                rv = ['a','b','c']
                return dict(result=rv, count=len(rv))
    @param name: 템플릿 함수명을 의미한다.
    @param begin: 템플릿 함수를 실행하기전에 처리할 것을 의미한다 (파라미터로를 입력으로 받는다)
    @param end: 템플릿 함수를 실행한후 실핼할것을 의미한다 (결과를 입력으로 받는다)
    @param exception : 예외처리가 발생했을때 실행할것을 의미한다 (exception, +  파라미터정보를 입력으로 받는다)
    @return: str 타입의 결과
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            before_fn = __templated_function_map.get(begin, None)
            after_fn = __templated_function_map.get(end, None)
            catch_fn = __templated_function_map.get(exception, None)
            render_template = __templated_function_map.get(name)
            if not render_template: raise Exception('not found template. (name=%s)' % (name, ))

            try:
                if before_fn: before_fn(*args, **kwargs)
            except Exception as e:
                print "[ERROR] @before execute failed.", e

            ## flask.route 실행
            try:
                ctx = f(*args, **kwargs)
            except Exception as e:
                catch_fn(exception=e, *args, **kwargs)

            try:
                if after_fn: after_fn(**ctx)
            except Exception as e:
                print "[ERROR] @after execute failed.", e

            if ctx is None:
                ctx = {}
            elif not isinstance(ctx, dict):
                return ctx
            text = render_template(**ctx)
            return render_template_string(text, **ctx)
        return decorated_function
    return decorator


def begin(name=None):
    """register에서 등록한 것을 사용할때 이용한다.
    이때, flask.route의 파라미터값을 그대로 사용한다.
    flask의 파라미터나 선처리를 할때 사용한다.

        사용예제:
            @app.route('/find')
            @begin('query_make')
            def find(param): ==> 이 결과 를 실행하기전에 선작업을 하고 싶을때 한다.
                rv = db.select(request.query)
                return dict(result=rv, count=len(rv))

    @param name:  등록한 함수 데잍레이터명을 의미한다.
    @return:
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            fn = __templated_function_map.get(name)
            if not fn:
                raise Exception('not found template. (name=%s)' % (name ,))
            try:
                fn(*args, **kwargs)
            except Exception as e:
                print "[ERROR] @before execute failed.", e
            rv = f(*args, **kwargs)
            return rv
        return decorated_function
    return decorator


def end(name=None):
    """register에서 등록한 것을 사용할때 이용한다.
    이때, flask.route에서 return한 값을 파라미터로 받는다.
    flask의 결과를 후킹하는 용도로 사용된다.

        사용예제:
            @app.route('/find')
            @end('json')
            def find():
                rv = ['a','b','c']
                return dict(result=rv, count=len(rv)) ==> 이 결과 뒤에 뭔가 추가작업을 하고 싶을때 한다.

    result, args, kwargs
    @param name:  등록한 함수 데잍레이터명을 의미한다.
    @return:
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            fn = __templated_function_map.get(name)
            if not fn:
                raise Exception('not found template. (name=%s)' % (name ,))
            rv = f(*args, **kwargs)
            try:
                fn(**rv)
            except Exception as e:
                print "[ERROR] @after execute failed.", e
            return rv
        return decorated_function
    return decorator


def exception(name=None):
    """register에서 등록한 것을 사용할때 이용한다.
    이때, 'exception=e' 형태의 값과 flask.route에서의 파라미터를 받는다.
    flask의 결과를 후킹하는 용도로 사용된다.

        사용예제:
            @app.route('/find')
            @exception('err_json')
            def find():
                rv = ['a','b','c']
                return dict(result=rv, count=len(rv)) ==> 이 결과 뒤에 뭔가 추가작업을 하고 싶을때 한다.

    @param name:
    @return:
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            fn = __templated_function_map.get(name)
            if not fn:
                raise Exception('not found template. (name=%s)' % (name ,))
            try:
                rv = f(*args, **kwargs)
            except Exception as e:
                fn(exception=e,*args, **kwargs)
            return rv
        return decorated_function
    return decorator