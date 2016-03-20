#-*- coding: utf-8 -*-
from bson.objectid import ObjectId
from flask import request, Blueprint, render_template
from flask_dmango import Dmango, RequestDmango

dmango_admin = Blueprint('dmango_admin', __name__, template_folder='../templates')

@dmango_admin.route("/")
def index():
    return render_template('admin/authors.html', test='testdddd')

@dmango_admin.route("/summary")
def summary():
    test = '1'
    return render_template('', test=test)

@dmango_admin.route("/server")
def server_list():
    return 'server_list'

@dmango_admin.route("/<server>.<db_name>.<collection_name>/list")
def contents_list(server, db_name, collection_name):
    q = request.dmango
    mongo = Dmango.find_collection(server, db_name=db_name, collection_name=collection_name)
    if q.id:
        rv = mongo.find(match={'_id': q.id})
        head_list = mongo.find(match={'_id': q.id})
        count = mongo.count(match={'_id': q.id})
    else:
        rv = mongo.find(match=q.match, sort=q.sort, start_idx=q.start_idx, end_idx=q.end_idx)
        head_list = mongo.find(match=q.match, sort=q.sort, start_idx=q.start_idx, end_idx=q.end_idx)
        count = mongo.count(match=q.match)
    # return dict(total=count,  page_num=q.page_num, page_size=q.page_size, result=rv)
    header = dict()
    for row in head_list:
        header.update({k: True for k in row})

    return render_template('admin/contents_list.html', header=header.keys(), result=rv, total=count,
                           page_size=q.page_size, page_num=q.page_num, max_page=int(count/q.page_size)+1)

@dmango_admin.route("/<server>.<db_name>.<collection_name>/detail/<_id>")
def detail(server, db_name, collection_name, _id):
    mongo = Dmango.find_collection(server, db_name=db_name, collection_name=collection_name)
    doc = mongo.find_one({'_id': ObjectId(_id)})
    return render_template('admin/detail.html', data_types={}, result=doc if doc else dict())
