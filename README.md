# flask-dmango

코딩은 최소화하여 서비스개발에 집중 할 수 있도록 지원하기 위해,
드망고는 특별한 코딩이나 노력없이, restful-api와 admin기능을 제공하는것을 목적으로 합니다.
참고로, 드망고는 flask와 mongodb(flask.ext.pymongo)를 연동하여 구현하였습니다.

단, 0.3.0 버전에서는 admin기능은 개발되지 않았습니다.


## 1. 소개

### restful API는 공짜 !

아래와 같이 mongodb의 접속정보만 입력해주면, 아래의 주소로 restful형태의 api사용이 가능해집니다.
http://127.0.0.1:5000/dmango/server1

```
from flask import Flask, current_app, Blueprint, request
from flask.ext.dmango import Dmango

app = Flask(__name__)
dmango = Dmango(app)
dmango.register_mongodb('server1', URI = 'mongodb://user_id:password@ds051459.mongolab.com:51459/database')

if __name__ == '__main__':
    app.run()
```


### MongoDB의 편리한 지원

register_mongodb로 등록한 몽고디비는 Dmango.find_mongodb() 을 통해 blueprint를 이용하여 구현한다면, 
몽고디비의 connection을 쉽게 불러 올수 있습니다. 

```
from flask import Blueprint
from flask.ext.dmango import Dmango

bp = Blueprint('name1', __name__)

@bp.route('/')
def index():
    db = Dmango.find_mongodb('server1')
    result = db["collection_name"].find({"title": "제목"})
    render_template('index.html', data=result, total=count)
```


### 편리한 쿼리 생성 지원

복잡한 몽고디비의 json형태의 쿼리를 몇가지 규칙을 통해 더 쉽게 생성 할 수 있도록 지원합니다.
이 규칙은 기본으로 제공하는 restful api를 사용할 때 꼭 알아둬야 합니다

```
from flask.ext.dmango import DmangoQueryBuilder

b = DmangoQueryBuilder()
b.query("title__ilike", 'apple')
b.query("price__gte:int", 5000)
b.query("code__in", ['food', 'digital'])
print b() 

==> {'price': {'$gte': 5000}, 'code': {'$in': ['food', 'digital']}, 'title': /apple/i }
```



## 2. RestFul API (들어가기전)

드망고의 ResultFul API 주소형식은 다음과 같습니다.

http://127.0.0.1:5000/dmango/server명.db명.collection명/명령어?필드명__메소드:필드타입=값&...


### 2.1 DB리스트 보기 (예: http://127.0.0.1:5000/dmango/server명)

서버명만 넣었을 경우는 해당 서버에 존재하는 database 목록을 던져줍니다.

```json
{
            "status": 200,
            "api_name": "show_dbs",
            "db_names": [
               "cx",
               "sada9_dev",
               "local"
            ],
            "msg": "성공",
            "total": 3,
            "server": "sada9_api"
}
```

2.2 collection 리스트 보기 

예: http://127.0.0.1:5000/dmango/server명.db명
서버명과 DB명을 넣었을 경우는 해당 서버의 DB에 존재하는 collection 목록을 던져줍니다.

```js
{
            "status": 200,
            "api_name": "show_dbs",
            "db_names": [
               "sada9_dev",
               "local"
            ],
            "msg": "성공",
            "total": 3,
            "server": "sada9_api"
}
```

### 2.3 명령어 보기 

예: http://127.0.0.1:5000/dmango/server명.db명.collection명
      서버명과 DB명 그리고 collection명을 모두 입력한 경우는 드망고에서 지원가능한 명령어 정보가 보여집니다.

```
{
       "result": [
          {
            "name": "param", 
            "comment": "파라미터가 올바르게 만들어 지는지 테스트하기 위해서 사용", 
            "url": "./server1.sada9_dev.testdb/param"
          }, 
          {
            "name": "find_one", 
            "comment": "한건만 검색할때 사용한다. 단, _id 조건이 있으면 나머지는 무시됨", 
            "url": "./server1.sada9_dev.testdb/find_one"
          }, 
          ...  생략  ....
          {
            "name": "string_group", 
            "comment": "특정 필드를 그룹핑하여 카운팅해준다. _group= 이라는 값을 사용한다.", 
            "url": "./server1.sada9_dev.testdb/string_group"
          }
       ], 
       "status": 200, 
       "api_name": "api_list", 
       "msg": "성공", 
       "time(ms)": 0, 
       "total": 11
}
```



## 3. RestFul API (명령어알기)

드망고의 ResultFul API 에서 "서버.디비.콜렉션"을 모두 입력한 경우 명령어를 사용할 수 있다. 지원되는 명령어는 다음과 같다.

명령어 |	설명	| 예제
--- | --- | ----
param	|파라미터가 올바르게 만들어 지는지 테스트하기 위해서 사용한다.	 | .
find_one	|한건만 검색할때 사용한다. 단, _id 조건이 있으면 나머지는 무시된다 특이 사항으로는 _page_num=1 _page_size=10 같은 페이징 기능도 적용가능하다.	
find	|일반적인 검색을 할 때 사용한다	 | .
count	| 검색결과가 몇건인지 확인하기위해 사용 |	.
insert|	데이터를 저장하기위해 사용한다. 단, 필드명이 _로 시작되는 값은 무시된다	 | .
save|	데이터를 저장하기위해 사용한다. insert 와의 차이점은 _id 가 허용되며, 같은 _id를 만나면  update 처리된다	|.
update|	_id로 1건의 데이터만 찾아 update 가 가능하다. (즉, where조건은 _id만 가능하고 나머지는 변경되는 값이다)	|.
remove|	_id 로 찾은 데이터를 삭제한다 (여러건의 데이터를 삭제하는것은 지원하지 않는다)	|.
push|	_id 로 찾은 데이터에서 list 타입의 값에 데이터를 append 할때 사용한다. | id=id값&cate_nm=추가할값	
inc|	_id 로 찾은 데이터에서 특정 필드의 값을 증가시켜준다. 보통 조회수 update할때 사용한다. | /dmango/server.db.collection/inc?id=id값&clk_cnt=1	
string_group|	필드를 그룹핑하여 카운팅해준다. 그룹대상이 되는 필드는 _group 이라는 예약어를 사용하며, list타입의 필드를 풀어서 그풉핑 해야 한다면, _unwind 라는 예약어가 존재한다. | /dmango/server.db.collection/string_group?_group=cate_nm&_unwind=cate_nm




## 4. Dmango 파라미터 알기

드망고에서는 서버에서 쿼리를 생성하지 않고, GET 형태로 사용자가 직접 쿼리를 생성하는 방식으로 자유롭게 데이터를 저장하는것을 지원한다.
명령어를 사용하기 위해서는 데이터를 표현하는 "Dmango파라미터"에 대한 사용법을 알아야 한다.

* 구조 :  필드명__메소드:타입=값
* 예제 : product__ilike:string=셀카봉


### 4.1 필드명
mongodb의 필드명을 의미한다. (스키마의 필드명을 의미한다.)

### 4.2 메소드
검색조건의 오퍼레이션을 의미한다. 데이터를 like검색하거나 범위 검색을 하고 싶을때 이용한다.

메소드명	|설명	
--- | ---
like |	좌우절단 검색을 의미한다. like 검색을 생각하면 된다.	 
ilike |	like와 유사하고, 다른점은 대소문자를 구분하지 않는다	
gt	 |특정값보다 크다를 의미한다. (val > 100)	
lt	 |특정값보다 작다를 의미한다. (val < 100)	
gte	 |특정값보다 크거나 같음을 의미한다 (val >= 100)	
lte	 |특정값보다 작거나 같음은 의미한다 (val <= 100)	
in	 |값이 포함되었는지 의미한다. val in (값1, 값2 ...)	
nin	 |값이 포함되지 않았는지 의미한다. 단 N개의 값이 지원된다. val not in (값1, 값2...)	
ne	 |not equals ( val != 값)	
startswith	 |문자열이 특정값으로 시작하는지 찾는다	
endswith |	문자열이 특정값으로 끝나는지 찾는다	
istartswith	 |startswith에서 대소문자를 구분하지 않는다	
iendswith	 |endswith에서 대소문자를 구분하지 않는다	
between	 |범위값을 의미한다. gte와 lte를 사용하는것과 동일하다. <br/>유용한 점은 value의 크기에 따라 gte와 lte가 알아서 붙인다는 점이 다르다.<br/> price__between=200&price__between=100 ==> {price: {$lte:"200", $gte:"100"}<br/>
price__between=50&price__between=110 ==> {price: {$lte:"50", $gte:"110"} 


생략했을때는 exact와 같다고 보면되며, insert, update를 위해서 사용되는 필드는 메소드를 붙이면 안된다.	


### 4.3 타입 (데이터 타입)
데이터 타입을 의미한다. int, string 같은 데이터 타입을 의미한다.
request받는 값에서는 데이터 타입을 알수 없고, 몽고디비에서 데이터 타입을 지정해야 하는 경우를 위해 사용된다.
예를 들어, price=100 으로 값을 받으면, 100은 string형으로 받게되어 숫자형 값과 비교할때 문제가 발생된다.
이럴때, price:int=100 과 같이 타입을 지정해 줄 수 있다.

필드타입	| 설명	
--- | --- 
int	| 정수형 	 숫자	
long		| 정수형 숫자	
float	| 	소숫점형 숫자	
string, text, str	| 	문자열을 의미한다.		| .
json	| 	json으로 변환한다. 필드명은 꼭 "" 를 넣어 규칙에 맞춰야한다.		
datetime	| 	datetime형으로 변환한다. yyyymmddhhmiss 형태의 문자열로 표현한 값을 변환한다.		
list	| 	콤마(,) 로 구분된 문자열을 list로 변환한다. (내부적으로는 split(",") 한다고 보면된다)		
dict	| 	json과 동일하다		
oid		| ObjectID 타입을 의미한다		


4.4.값
저장될 값을 의미한다. GET형태에서 받는 value와 동일하다.
특별한 기능으로는 $today 가 존재한다. (yyyymmdd 형태의 오늘날짜를 문자열로 자동변환된다.)

5. 예약어
드망고의 필드표현에서는 예약어는 _로 시작하는 값이다.
주소 find나 string_group 같은 조회할때 섞어서 사용하는경우가 많다.

* _page_num : 페이징처리를 할 때 사용된다. (string_group, find 명령에서 사용)
* _page_size: 페이징처리를 할 때 사용된다. (string_group, find 명령에서 사용)
* _start_offset : 페이징처리를 할 때 사용된다. _page_num과 같이 사용한다면 offset값이 우선된다.
* _end_offset : 페이징처리를 할 때 사용된다. _page_size과 같이 사용한다면 offset값이 우선된다.
* _fields : db쿼리의 select문과 같다. 조회할 대상의 필드를 제약할때 사용된다. &_fields=product_nm,price 를 추가하면 해당 필드의 결과만 리턴된다.
* _options: 드망고의 옵션을 의미한다. 현재는 json결과에 개행을 할지 안할지 조정하는 indent만 존재한다. (예: _options=indent:true )
* _group : 그룹핑할 필드를 의미한다. string_group 에서만 사용된다.
* _unwind : 그룹핑할 에서 list타입이어서 아이템을 풀어야할 필드를 의미한다. string_group 에서만 사용된다.
* _exclude_query_fields : 쿼리로 유도되면 안되는 필드를 의미한다. 예를 들어, 로깅목적으로 사용하는 더미값이 쿼리로 유도되지 않기를 희망할때 사용한다. (예: _exclude_query_fields=user_id)
* _sort : 정렬을 할때 사용된다. 필드명__desc , 필드명__asc 형태로 사용한다 (예: _sort=price__desc )


### 6. 예제로 보는 restful API 사용

6.1 price 필드는 숫자값이고 1000 ~ 2000인 값을 조회하고자 할때
==> /find?price__gte:int=1000&price__lte:int=2000

6.2 title에 "구두"가 포함된 제품을 찾아 category로 그룹핑
==> /string_group?title__ilike=구두&_group=category

6.3 title이나 category에 의류가 포함된 상품을 100개만 보고자 할때
==> /find?title,category__ilike=의류&_page_size=100

6.4 "6.3"의 결과를 보기좋게 개행해서 보고싶을때
==> /find?title,category__ilike=의류&_page_size=100&_options=indent:true

6.5 {title: "셀카봉 신품", price: 4500, cate_nm : ["생활용품", "특가"], cate_cd : [4, 6]} 을 저장하려면?
==> /insert?title=셀카봉 신품&price:int=4500&cate_nm:list=생활용품,특가&cate_cd:json=[4, 6]
==> /insert?title=셀카봉 신품&price:int=4500&cate_nm=생활용품&&cate_nm=특가&cate_cd:int=4&cate_cd:int=6
==> 다양한 표현이 더 존재함.
