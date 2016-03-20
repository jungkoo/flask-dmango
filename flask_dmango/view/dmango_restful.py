#-*- coding: utf-8 -*-
from flask import request, Blueprint, url_for, redirect
from flask_dmango import Dmango
from flask_dmango.request_helpers import RequestDmango
from flask_dmango.view import dmango_api_template

dmango_restful = Blueprint('dmango_restful', __name__)


@dmango_restful.route('/<server>.<db_name>.<collection_name>/xxx', methods=['GET', 'POST'])
@dmango_api_template(api_name='xxx', indent=True)
def xxx(server=None, db_name=None, collection_name=None):
    return dict(match='xxx')


@dmango_restful.route('/<server>/', methods=['GET', 'POST'])
@dmango_api_template(api_name='show_dbs')
def show_dbs(server):
    db_list = Dmango.find_mongodb(server).cx.database_names()
    return dict(server=server, total=len(db_list), db_names=db_list)

@dmango_restful.route('/<server>.<db_name>/', methods=['GET', 'POST'])
@dmango_api_template(api_name='show_collecitons')
def show_collections(server, db_name):
    collection_list = Dmango.find_mongodb(server).cx[db_name].collection_names()
    return dict(server=server, total=len(collection_list), db_names=collection_list)


@dmango_restful.route('/<server>.<db_name>.<collection_name>/', methods=['GET', 'POST'])
@dmango_restful.route('/<server>.<db_name>.<collection_name>/api_list', methods=['GET', 'POST'])
@dmango_api_template(api_name='api_list')
def api_list(server, db_name, collection_name):
    url = lambda x: "./%s.%s.%s/%s" % (server, db_name, collection_name, x)
    contents = lambda name, comment: dict(name=name, url=url(name), comment=comment)
    r = (
        contents('param', '파라미터가 올바르게 만들어 지는지 테스트하기 위해서 사용'),
        contents('find_one', '한건만 검색할때 사용한다. 단, _id 조건이 있으면 나머지는 무시됨'),
        contents('find', '일반적인 검색을 할 때 사용한다.'),
        contents('count', '검색결과가 몇건인지 확인하기위해 사용'),
        contents('insert', '데이터를 저장하기위해 사용한다. 단, 드망고의 명령어는 사용하지 말자'),
        contents('save','데이터를 저장하기위해 사용한다. '
                                'insert 와의 차이점은 _id 가 허용되며, 같은 _id를 만나면  update 처리됨'),
        contents('update', '_id로 1건의 데이터만 찾아 update 가 가능하다.'),
        contents('remove', '_id 로 찾은 데이터를 삭제한다.'),
        contents('push', '_id 로 찾은 데이터에서  list 타입에 값을 하나 append 할때 사용'),
        contents('inc', '_id 로 찾은 데이터에서  넘겨받은 필드와 숫자값만큼 증가시켜준다.'),
        contents('string_group', '특정 필드를 그룹핑하여 카운팅해준다. _group= 이라는 값을 사용한다.'),
    )
    return dict(total=len(r), result=r)


@dmango_restful.route('/<server>.<db_name>.<collection_name>/find_one', methods=['GET', 'POST'])
@dmango_api_template(api_name='find_one')
def find_one(server, db_name, collection_name):
    q = request.dmango
    mongo = Dmango.find_collection(server, db_name=db_name, collection_name=collection_name)
    if q.id:
        rv = mongo.find_one(match={'_id': q.id}, fields=q.fields)
        count = mongo.count(match={'_id': q.id})
    else:
        rv = mongo.find_one(match=q.match, fields=q.fields)
        count = mongo.count(match=q.match)
    return dict(total=count, result=rv)


@dmango_restful.route('/<server>.<db_name>.<collection_name>/param', methods=['GET', 'POST'])
@dmango_api_template(api_name='param', indent=True)
def index(server=None, db_name=None, collection_name=None):
    q = request.dmango
    return dict(match=q.match, sort=q.sort, unwind=q.unwind, group=q.group,
                start_idx=q.start_idx, end_idx=q.end_idx, page_num=q.page_num, page_size=q.page_size,
                server=server, db=db_name, collection=collection_name, fields=q.fields, options=q.options
                )

@dmango_restful.route('/<server>.<db_name>.<collection_name>/find', methods=['GET', 'POST'])
@dmango_api_template(api_name='dmango_find')
def find(server, db_name, collection_name):
    q = request.dmango
    mongo = Dmango.find_collection(server, db_name=db_name, collection_name=collection_name)
    if q.id:
        rv = mongo.find(match={'_id': q.id}, fields=q.fields)
        count = mongo.count(match={'_id': q.id})
    else:
        rv = mongo.find(match=q.match, sort=q.sort, fields=q.fields, start_idx=q.start_idx, end_idx=q.end_idx)
        count = mongo.count(match=q.match)
    return dict(total=count,  page_num=q.page_num, page_size=q.page_size, result=rv)

@dmango_restful.route('/<server>.<db_name>.<collection_name>/count', methods=['GET', 'POST'])
@dmango_api_template(api_name='dmango_count')
def count(server, db_name, collection_name):
    q = request.dmango
    if q.id:
        raise Exception('find method is "_id" value not support.')
    mongo = Dmango.find_collection(server, db_name=db_name, collection_name=collection_name)
    count = mongo.count(match=q.match)
    return dict(total=count)

@dmango_restful.route('/<server>.<db_name>.<collection_name>/insert', methods=['GET', 'POST'])
@dmango_api_template(api_name='dmango_insert')
def insert(server, db_name, collection_name):
    q = request.dmango
    mongo = Dmango.find_collection(server, db_name=db_name, collection_name=collection_name)
    rv = mongo.insert(q.match)
    return dict(result=rv)

@dmango_restful.route('/<server>.<db_name>.<collection_name>/save', methods=['GET', 'POST'])
@dmango_api_template(api_name='dmango_save')
def save(server, db_name, collection_name):
    q = request.dmango
    q = q.match.update(q.id)
    mongo = Dmango.find_collection(server, db_name=db_name, collection_name=collection_name)
    rv = mongo.save(q)
    return dict(result=rv)

@dmango_restful.route('/<server>.<db_name>.<collection_name>/update', methods=['GET', 'POST'])
@dmango_api_template(api_name='dmango_update')
def update(server, db_name, collection_name):
    q = request.dmango
    mongo = Dmango.find_collection(server, db_name=db_name, collection_name=collection_name)
    rv = mongo.update(q.id, q.match)
    return dict(result=rv)

@dmango_restful.route('/<server>.<db_name>.<collection_name>/push', methods=['GET', 'POST'])
@dmango_api_template(api_name='dmango_push')
def push(server, db_name, collection_name):
    q = request.dmango
    mongo = Dmango.find_collection(server, db_name=db_name, collection_name=collection_name)
    rv = mongo.push(q.id, q.match)
    return dict(result=rv)

@dmango_restful.route('/<server>.<db_name>.<collection_name>/inc', methods=['GET', 'POST'])
@dmango_api_template(api_name='dmango_inc')
def inc(server, db_name, collection_name):
    q = request.dmango
    mongo = Dmango.find_collection(server, db_name=db_name, collection_name=collection_name)
    rv = mongo.inc(q.id, q.match)
    return dict(result=rv)

@dmango_restful.route('/<server>.<db_name>.<collection_name>/remove', methods=['GET', 'POST'])
@dmango_api_template(api_name='dmango_remove')
def remove(server, db_name, collection_name):
    q = request.dmango
    if not q.id:
        raise Exception('_id값이 비어있습니다')
    mongo = Dmango.find_collection(server, db_name=db_name, collection_name=collection_name)
    rv = mongo.remove(q.id)
    return dict(result=rv)


@dmango_restful.route('/<server>.<db_name>.<collection_name>/string_group', methods=['GET', 'POST'])
@dmango_api_template(api_name='dmango_string_group')
def string_group(server, db_name, collection_name):
    """
    http://localhost:5000/dmango/server1.sada9_dev.testdb/string_group?_group=cate_nm&_unwind=cate_nm&_page_num=2&_page_size=5
    @param server:
    @param db_name:
    @param collection_name:
    @return:
    """
    q = request.dmango
    mongo = Dmango.find_collection(server, db_name=db_name, collection_name=collection_name)
    limit = q.end_idx + 1
    rv = mongo.string_group(q.match, group_fields=q.group, limit=limit, unwind_fields=q.unwind)
    return dict(result=rv[q.start_idx:])