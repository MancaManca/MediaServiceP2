from kivy import Logger
from collections import OrderedDict
from Crypto.Hash import SHA256
import requests


class ApiContentError(Exception):
    """An API Content Error Exception"""

    def __init__(self, content):
        self.content = content

    def __str__(self):
        return "ApiContentError: content={}".format(self.content)


class ApiError(Exception):
    """An API Error Exception"""

    def __init__(self, status):
        self.status = status

    def __str__(self):
        return "ApiError: status={}".format(self.status)


class Api:

    def __init__(self, name):
        self.name = name

    def _url(self, path):
        return 'https://tv-v2.api-fetch.website' + path

    def get_search(self):
        self.query_str = '/'
        if 'page' not in self.query:
            self.page = '1'
            self.query_str += self.page + '?'
        else:
            self.query_str = self.query_str + self.query['page'] + '?'

        for i in self.query:
            if i != 'id' and i != 'page':
                self.query_str = self.query_str + str(i) + '=' + str(self.query[i]) + '&'

        self._url_prepared = self.url + self.query_str[:-1]

        try:
            return requests.get(self._url_prepared)
        except Exception as e:
            raise Exception(e)

    def get_search_by_id(self):
        self._url_prepared = self.short_url + self.query['_id']
        try:
            return requests.get(self._url_prepared)
        except Exception as e:
            raise Exception(e)

    def get_pages(self):
        try:
            return requests.get(self.url)
        except Exception as e:
            raise Exception(e)


class Movies(Api):
    def __init__(self, page=None, sort=None, order=None, keywords=None, _id=None, genre=None, **kwargs):

        self.url = self._url('/movies')
        self.short_url = self._url('/movie/')
        self.query = {}

        if page:
            self.query['page'] = page
            Logger.info('Movies API: page {}'.format(page))
        if sort:
            self.query['sort'] = str(sort).replace(' ', '%20')
            Logger.info('Movies API: sort {}'.format(str(sort).replace(' ', '%20')))
        if order:
            self.query['order'] = order
            Logger.info('Movies API: order {} '.format(order))
        if _id:
            self.query['_id'] = _id
            Logger.info('Movies API: _id {}'.format(_id))
        if genre:
            self.query['genre'] = genre
            Logger.info('Movies API: genre {}'.format(genre))
        if keywords:
            self.query['keywords'] = str(keywords).replace(' ', '%20')
            Logger.info('Movies API: keywords {}'.format(str(keywords).replace(' ', '%20')))


class Shows(Api):
    def __init__(self, page=None, sort=None, order=None, keywords=None, _id=None, genre=None, **kwargs):

        self.url = self._url('/shows')
        self.short_url = self._url('/show/')
        self.query = {}

        if page:
            self.query['page'] = page
            Logger.info('Shows API: page {}'.format(page))
        if sort:
            self.query['sort'] = str(sort).replace(' ', '%20')
            Logger.info('Shows API: sort {}'.format(str(sort).replace(' ', '%20')))
        if order:
            self.query['order'] = order
            Logger.info('Shows API: order {} '.format(order))
        if _id:
            self.query['_id'] = _id
            Logger.info('Shows API: _id {}'.format(_id))
        if genre:
            self.query['genre'] = genre
            Logger.info('Shows API: genre {}'.format(genre))
        if keywords:
            self.query['keywords'] = str(keywords).replace(' ', '%20')
            Logger.info('Shows API: keywords {}'.format(str(keywords).replace(' ', '%20')))


def api_request_handler(_response):
    if 'application/json' not in _response.headers['Content-Type']:
        raise ApiContentError('Error response type {}'.format(_response.headers['Content-Type']))
    if _response.status_code != 200:
        raise ApiError('Error occurred: {}'.format(_response.status_code))


def hash_item_m(x):
    to_hash = '{}'.format(x)
    hashed_item = SHA256.new(to_hash.encode()).hexdigest()
    return hashed_item


def hash_item(__json_in, method_flag): # requires JSON object
    __json_hashed_out = OrderedDict()
    # Logger.info('HashItem: json {}'.format(__json_in))

    if method_flag:
        # Logger.info('going for multi flag {}'.format(method_flag))
        for i in __json_in:

            hashed = hash_item_m(i['_id'])
            __json_hashed_out[hashed] = i
    else:
        # Logger.info('going for multi flag {}'.format(method_flag))
        hashed = hash_item_m(__json_in['_id'])
        __json_hashed_out[hashed] = __json_in

    return __json_hashed_out


def populate_hashed_json_dic(__json_hashed_in, db_instance, which):
    temp = OrderedDict()
    for i in __json_hashed_in:
        temp[i] = __json_hashed_in[i]

    db_instance._put(key=which, val=temp)
    # Logger.info('populated dic {}'.format(to_dic[which]))


def api_request_controler(_api_call_response, db_instance):

    if 'keywords' in _api_call_response.url:
        try:
            populate_hashed_json_dic(hash_item(_api_call_response.json(), True), db_instance, 'hashed_dic_search')
        except Exception as e:
            Logger.info('GetApi: Search failed duo to : {}'.format(e))
    else:
        try:
            if Shows().short_url in _api_call_response.url:
                populate_hashed_json_dic(hash_item(_api_call_response.json(), False), db_instance, 'hashed_dic_show')
        except Exception as e:
            Logger.errror('GetApi: Show failed duo to : {}'.format(e))
            pass
        try:
            if Movies().short_url in _api_call_response.url:
                populate_hashed_json_dic(hash_item(_api_call_response.json(), False), db_instance,'hashed_dic_movie')
        except Exception as e:
            Logger.error('GetApi: Movie failed duo to : {}'.format(e))
            pass
        try:
            if Movies().url in _api_call_response.url:
                populate_hashed_json_dic(hash_item(_api_call_response.json(), True), db_instance,'hashed_dic_movies')
        except Exception as e:
            Logger.error('GetApi: Movies failed duo to : {}'.format(e))
            pass
        try:
            if Shows().url in _api_call_response.url:
                populate_hashed_json_dic(hash_item(_api_call_response.json(), True), db_instance, 'hashed_dic_shows')
        except Exception as e:
            Logger.error('GetApi: Shows failed duo to : {}'.format(e))
            pass


def get_api(_api_call, db_instance):
    try:
        api_request_handler(_api_call)
        api_request_controler(_api_call, db_instance)
    except Exception as e:
        Logger.critical('GetApi: failed duo to : {}'.format(e))
        raise Exception
