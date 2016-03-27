# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from flask import Flask, Blueprint
from flask_dmango import Dmango

app = Flask(__name__)
dmango = Dmango(app)
dmango.register_mongodb('server1', URI='mongodb://sample:sample@ds035240.mlab.com:35240/dmango')


bp = Blueprint('name1', __name__)
bp2 = Blueprint('name2', __name__)


@bp.route('/')
def test1():
    return "sample"


@bp2.route('/t2')
def test2():
    c = Dmango.find_collection('server1', db_name='dmango', collection_name='johnkim')
    for row in c.find(end_idx=10):
        print "-----------------------"
        for k in row:
            print k, row[k]
    return 'ok'

app.register_blueprint(bp)
dmango.register_blueprint(bp2)


if __name__ == '__main__':
    app.run(debug=True)