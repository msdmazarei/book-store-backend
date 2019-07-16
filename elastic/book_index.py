from elastic.elastic_engine import es
from enums import str_genre, str_type
from repository.person_repo import fullname_persons, full_name_by_id

mapping = {
    'book': {'_timestamp': {
        'enabled': 'true'
    },
        'properties': {
            'title': {'type': 'text'},
            'genre': {'type': 'keyword'},
            'persons': {'type': 'nested'},
            'rate': {'type': 'float'},
            'pub_year': {'type': 'keyword'},
            'press': {'type': 'text'},
            'writer': {'type': 'text'},
            'language': {'type': 'keyword'},
            'type': {'type': 'keyword', 'index': 'not_analyzed'},
            'book_id': {'type': 'text', 'index': 'not_analyzed'},
            'description': {'type': 'text'},
            'tags': {'type': 'text'}
        }
    }
}

if not es.indices.exists('online_library'):
    es.indices.create('online_library')


def index_book(data, db_session):
    index_data = {
        'title': data.get('title', None),
        'genre': str_genre(data.get('genre', None)),
        'persons': fullname_persons(data.get('persons', None), db_session),
        'rate': data.get('rate', None),
        'pub_year': data.get('pub_year', None),
        'press': full_name_by_id(data.get('Press', None), db_session),
        'writer': full_name_by_id(data.get('Writer', None), db_session),
        'language': data.get('language', None),
        'type': str_type(data.get('type')),
        'tags': data.get('tags', None),
        'book_id': data.get('book_id', None),
        'description': data.get('description', None)
    }

    rs = es.index(index='online_library', doc_type='book', body=index_data, id=data.get('book_id'))
    print(rs)

    return {'msg': 'successful'}


def delete_book_index(book_id):
    if es.exists(index='online_library', doc_type='book', id=book_id):
        res = es.delete(index='online_library', doc_type='book', id=book_id)


def search_by_book_id(book_id):
    body = {'query': {'match': {'book_id': book_id}}}
    res = es.search(index='online_library', body=body)
    return res


def get(book_id):
    return es.get(index='online_library', id=book_id)


def search_phrase(search_phrase):
    result = []
    fields = get_fields_by_boost()
    es_res = es.search(index='online_library', body={'from': 0, 'size': 4, 'query': {
        'multi_match': {'query': search_phrase, 'type': 'most_fields', 'fields': fields, 'fuzziness': 'AUTO'}}})

    hits = es_res.get('hits',None)
    count =0
    if hits is not None:
        count = hits.get('total')
        if count > 0 :
            rs = hits.get('hits')
            for item in rs:
                result.append(item.get('_id'))
    return result


def get_fields_by_boost():
    fields = ['title^5', 'writer^4', 'press^3', 'persons^2', 'genre^3', 'tags^2', 'type^1', 'description', 'rate',
              'pub_year', 'language']
    return fields


def wildcard_es(search_phrase):
    result = []
    fields = get_fields_by_boost()
    es_res = es.search(index='online_library', body={'from': 0, 'size': 4, 'query': {'wildcard': {
        'title': {
            'value': 'my*s',
            'boost': 1.0,
            'rewrite': 'constant_score'
        }}}})
    return es_res


def query_string(search_phrase):
    res = es.search(index='online_library', body={'from': 0, 'size': 4, 'query': {'query_string': {
        'query': '*{}*'.format(search_phrase), 'fields': ['title^5', 'persons^5', 'genre']}}})

    return res
