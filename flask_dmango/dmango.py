# -*- coding: utf-8 -*-
"""
    flask-dmango
    ~~~~~~~~~~~~

    이 모듈은  flask.ext.pymongo , request parser, restful-api  를 기본으로 제공한다.
    Dmango 를 통해 mongodb 를 등록하게 되면, 기본적인 restful-API 가 제공된다고 보면된다.
    특별한 코딩없이 바로 데이터를 저장/삭제/검색이 가능하다.
    그리고 기본으로 admin 기능도 제공되어 데이터 관리기능까지 제공된다.

    :copyright: (c) 2014 by mincheol jeong
    :license: BSD, see LICENSE for more details.
"""
from flask_dmango import RequestDmango
from flask_dmango.mongodb_helpers import DmangoEngine
from flask_pymongo import PyMongo
from flask import current_app, request, Blueprint


class Dmango(object):
    def __init__(self, app, root_url='/dmango'):
        """
        dmango 의 기본  base 를 지정한다.

        @param app: Flask's app
        @param root_url: default root_url is '/dmango'
        @return: none
        """
        self.__root_url = root_url
        self.__app = app
        self.init_app(app)


    @staticmethod
    def find_mongodb(server_name):
        """
        서버명으로 Pymongo 객체를 찾는다.
        특이한건  current_app 의 드망고의 서버이름에서 찾기 때문에,  app 별로 관리된다.
        @param server_name: 등록한 서버명
        @return: 파이몽고 객체
        @rtype: PyMongo
        """
        if 'dmango' not in current_app.extensions:
            raise Exception('not exist app.extentions.dmango')
        return current_app.extensions['dmango'][server_name]

    @staticmethod
    def find_collection(server_name, db_name, collection_name):
        """ 드망고에 등록된 몽고디비정보를 찾아, 드망고 콜렉션 오브젝트를 받는다.
        find_mongodb에서 좀더 쉽게 콜렉션을 리턴받기위해 사용하는 메소드이다.

        @param server_name: 등록한 몽고디비 서버정보(서버명)
        @param db_name: 디비명
        @param collection_name: 콜렉션명
        @return: Dmango의 Collection객체
        @rtype: DmangoEngine
        """
        return DmangoEngine(Dmango.find_mongodb(server_name), db_name, collection_name)

    def init_app(self, app):
        if 'dmango' not in app.extensions:
            app.extensions['dmango'] = dict()  # {mongo_name: pymongo}

        print '[DMANGO] restfulAPI loading...'
        from flask_dmango.view.dmango_restful import dmango_restful
        self.register_blueprint(dmango_restful, url_prefix=self.__root_url)
        print '[DMANGO] help loading...'
        from flask_dmango.view.dmango_help import dmango_help
        self.register_blueprint(dmango_help, url_prefix=self.__root_url+"_help")
        print '[DMANGO] Admin Blueprint loading...'
        from flask_dmango.view.dmango_admin import dmango_admin
        self.register_blueprint(dmango_admin, url_prefix=self.__root_url+"_admin")


    def register_mongodb(self, server_name, **options):
        """
        몽고디비의 정보를 등록한다.
        flask.ext.pymongo 를 이용하여 등록하므로,  app.config 에  options 가 등록된다.
        이때 server_name 이 헤더가 되어 등록되어 진다.
        그러므로,  app 별로  server_name 이름이 겹쳐지는것은  허용되지 않는다.

        @param server_name: 나중에 몽고디비 접근정보를 찾기위한  key 로 사용된다.
        @param options:  mongodb 의 접속 정보를 의미한다.  URI=..., PORT..
        @return: None
        """
        if not server_name:
            raise Exception('name is not empty.')
        if options:
            key = lambda o: '%s_%s' % (server_name, o)
            print "[DAMNGO] mongodb connection info, " , {key(k): options[k] for k in options}
            self.__app.config.update({key(k): options[k] for k in options})
        try:
            if server_name in self.__app.extensions['dmango']:
                raise Exception('duplicate dmango name. "%s"' % server_name)
            self.__app.extensions['dmango'][server_name] = PyMongo(self.__app, server_name)
        except Exception as e:
            raise Exception('connection failed. (%s)' % (e,))

    def register_blueprint(self, blueprint, **option):
        assert blueprint , Blueprint
        """
        app.register 의 기능을 대행해 준다.
        다른점은  dmango 의  reqeust를 파싱한 결과가 기본으로 붙여준다는점만 다르다.
        flask 의  reqeust 객체에 다음과 같은 정보가 붙는점이 다르다. (불필요하면  app 에서 바로  blueprint 를 붙이도록 한다)

        예제)
            request.dmango_query   :   builder.Query 객체를 리턴함.
            request.dmango_options :   builder.Option  객체를 리턴함.

        @param blueprint: 등록할 블루프린터를 의미한다.
        @param option: app.register_blueprint 와 동일한 옵션을 의미한다.
        @return: none
        """
        def __bind_request_query():
            setattr(request, 'dmango', RequestDmango(request))
        blueprint.before_request(__bind_request_query)
        self.__app.register_blueprint(blueprint, **option)
