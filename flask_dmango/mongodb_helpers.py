# -*- coding: utf-8 -*-
import datetime as datetime_lib
from flask_pymongo import PyMongo
from pymongo import MongoClient, MongoReplicaSetClient
from flask_dmango.query.fields import to_variable, to_dmango_field_info


class QueryBuilder:
    def __init__(self):
        self._query = {}

    def exist_and(self):
        return '$and' in self._query

    def is_empty(self):
        return len(self._query) <= 0

    def append(self, query):
        if query is None:
            return self
        if isinstance(query, QueryBuilder):
            query = query()
        if not isinstance(query, dict):
            raise TypeError('append method type is [dict]')

        for k in query:
            key = k
            value = query.get(k)
            if self.is_empty():
                self._query.update({key: value})
            elif self.exist_and():
                is_update = False
                for row in self._query['$and']:
                    if QueryBuilder.multi_check_and_update(key, value, row):
                        is_update = True
                        break
                if not is_update:
                    self._query['$and'].append({key: value})
            elif not self.exist_and():
                if not QueryBuilder.multi_check_and_update(key, value, self._query):
                    self._query = {'$and': [self._query, {key: value}]}
        return self

    def clear(self):
        self._query.clear()

    """
    price : {$gt:100}
    price : {$gt:100, dd}
    """
    @staticmethod
    def multi_check_and_update(key, value, m):
        if isinstance(m, dict) and key not in m: # 해당안에 겹치는 키가 업으면 기냥 깽겨넣음.
            m.update({key: value})
            return True
        if isinstance(value, dict) and isinstance(m.get(key), dict) and len(value) == 1:
            # 해당안에 겹쳐지는걸 찾으면 그안에 낑겨서  update.
            my_method = value.keys()[0]
            if not my_method in m[key]:
                m[key].update(value)
                return True
        return False

    def __call__(self):
        return self._query if len(self._query) > 0 else None

    def __str__(self):
        return self._query.__str__()

    def __len__(self):
        return len(self._query)


class DmangoQueryBuilder:
    def __init__(self):
        self._query = QueryBuilder()

    def clear(self):
        self._query.clear()

    def append(self, query):
        if isinstance(query, (QueryBuilder,DmangoQueryBuilder)):
            self._query.append(query())
        elif isinstance(query, dict):
            self._query.append(query)
        else:
            raise TypeError('append method type is [dict | QueryBuilder | DmangoQueryBuilder]')

    def query(self, dmango_field_name, values, default_value=None):
        self._query.append(dmango_query(dmango_field_name, values, default_value))
        return self

    def __call__(self, *args, **kwargs):
        return self._query()

    def __len__(self):
        return len(self._query)

    def __str__(self):
        return str(self._query())


class DmangoEngine:
    """
    드망고에서 관리되는 몽고디비 실행 엔진이다.
    """
    def __init__(self, connection, db_name=None, collection_name=None):
        if not isinstance(connection, (PyMongo, MongoClient, MongoReplicaSetClient)) or not connection:
            raise TypeError('connection must be a class of PyMongo | MongoClient | MongoRepliaceSetClient.')
        self.__connection = connection
        self.__db_name = None
        self.__collection_name = None
        self.change(db_name, collection_name)

    def change(self, db_name=None, collection_name=None):
        if db_name:
            self.__db_name = db_name
        if collection_name:
            self.__collection_name = collection_name
        return self

    @property
    def connection(self):
        return self.__connection

    @connection.setter
    def connection(self, value):
        self.__collection_name = value

    @property
    def collection(self, db_name=None, collection_name=None):
        _db_name = db_name or self.__db_name
        _cn_name = collection_name or self.__collection_name
        if not _cn_name:
            raise TypeError('collection name is empty.')

        if isinstance(self.__connection, PyMongo):
            return self.__connection.cx[_db_name][_cn_name] if _db_name else self.__collection_name.db[_cn_name]
        else:
            return self.__connection[_db_name][_cn_name]

    def find(self, match={}, sort=None, start_idx=0, end_idx=20, fields=None):
        c = self.collection

        if fields:
            fields = {f:True for f in fields}

        c = c.find(match, projection=fields)

        if not c:
            return list()
        if sort:
            c = c.sort(sort)

        if end_idx >= 0:
            c = c[start_idx:end_idx+1]
        elif end_idx < 0:
            raise ValueError('ValueError: page_num or page_size by <= 0')
        else:
            c = c[start_idx:]
        return c

    def find_one(self, match, sort=None, fields=None):
        c = self.collection
        c = c.find_one(match, fields=fields if fields else None)
        if sort:
            c = c.sort(sort)
        return c

    def string_group(self, match, group_fields, limit=100, unwind_fields=None, filter_query=None):
        c = self.collection
        match_query = [{k: {'$exists': 'true'}
                                           for k in (group_fields
                                                     if isinstance(group_fields, (list, tuple))
                                                     else (group_fields,))}]
        if match:
            match_query.append(match)
            q = [{'$match': {'$and': match_query}}]
        else:
            q = [{'$match': match_query[0]}]

        for uw in unwind_fields if unwind_fields else tuple():
            q.append({'$unwind': '$%s' % uw})
        q.append({'$group': {'_id': {k: '$%s' % (k,)
                          for k in (group_fields
                                    if isinstance(group_fields, (list, tuple))
                                    else (group_fields,))}, 'count': {'$sum': 1}}})
        if filter_query:
            q.append(filter_query)
        q.append({'$sort': {'count': -1}})
        q.append({"$limit": limit})
        rv = c.aggregate(q)
        if u'result' in rv:
            rv = rv.get(u'result', tuple())

        for row in rv:
            row.update(row[u'_id'])
            del row[u'_id']
        return rv

    def count(self, match):
        c = self.collection
        c = c.find(match).count()
        return c

    def insert(self, data_json, w=1):
        """
        입력모드
        :param data_json: 저장할 json
        :param w: 0 - 빠르지만 안정성보장 안함, 1-어느정도 안정성 보장
        :return:
        """
        c = self.collection
        return c.insert(data_json if not isinstance(data_json, (list,)) else [data_json], w=w)

    def save(self, data_json):
        c = self.collection
        return c.save(data_json)

    def update(self, _id, set_json):
        c = self.collection
        return c.update({'_id': _id}, {'$set': set_json})

    def remove(self, _id):
        c = self.collection
        return c.remove({'_id': _id})

    def inc(self, _id, data_json):
        c = self.collection
        return c.update({'_id': _id}, {'$inc': {k: int(data_json.get(k, 1)) for k in data_json}})

    def push(self, _id, data_json):
        c = self.collection
        return c.update({'_id': _id}, {'$push': data_json})


def convert_dmango_special_values(values):
    today = datetime_lib.date.today()
    con_fn_dict = {
        "$sysdatetime": lambda: datetime_lib.datetime.today(),
        "$sysdate": lambda: today,
        "$today": lambda: "%d%02d%02d" % (today.year, today.month, today.day),
    }
    if not values:
        return None
    if isinstance(values, (str, unicode)) and str(values) in con_fn_dict:
        return con_fn_dict[str(values)]()
    if isinstance(values, (list, tuple)):
        for idx, row in enumerate(values):
            if isinstance(row, (str,unicode)) and str(row) in con_fn_dict:
                values[idx] = con_fn_dict[str(row)]()
    return values


find_field_end_idx_fn = lambda text, delis: min(text.find(d) if text.find(d) > 0 else len(text) for d in delis)

def dmango_query(dmango_field_name, values, default_value=None):
    if not isinstance(values, (int, float, long)):
        values = values if values and len(values) > 0 else default_value

    field_end_idx = find_field_end_idx_fn(dmango_field_name,  ('__', ':', '~'))
    field_name = dmango_field_name[:field_end_idx]
    if field_name.find(",") < 0:
        query = to_variable(to_dmango_field_info(dmango_field_name), convert_dmango_special_values(values))
    else:  # 콤마로 구분된 쿼리 구조 or 쿼리를 처리한다. (예: title,name=키워드 )
        tail_info_str = dmango_field_name[field_end_idx:]
        _sub_q = []
        for f in field_name.split(","):
            _q = to_variable(to_dmango_field_info(f+tail_info_str), convert_dmango_special_values(values))
            if _q:
                _sub_q.append(_q)
        query = {"$or": _sub_q} if len(_sub_q) > 0 else None

    return query


if __name__ == '__main__':
    b = DmangoQueryBuilder()
    b.query("title", ['apple','ttt'])
    b.query("price__gte:int", 5000)
    b.query("name,jmc__ilike", "jmc")
    print b

