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
__version__ = '0.0.3-dev'
from .mongodb_helpers import DmangoEngine, dmango_query, QueryBuilder, DmangoQueryBuilder
from .request_helpers import RequestDmango, AbstractRequestDmango
from .dmango import Dmango