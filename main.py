from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.properties import ObjectProperty, BooleanProperty, StringProperty, partial
from kivy.uix.accordion import Accordion, AccordionItem
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import AsyncImage, Image
from kivy.uix.modalview import ModalView
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.scrollview import ScrollView
from kivy.utils import get_color_from_hex
from kivy import Logger
from collections import OrderedDict
import json
from Crypto.Hash import SHA256
import requests
import socket
import threading

"""SCAN"""


def scan_network_for_single_connection(_subnet):
    Logger.info('Network scanning initializes on thread {}'.format(threading.currentThread().getName()))

    network_address = '192.168.0.{}'.format(_subnet)
    Logger.info('Scanner for {}'.format(network_address))
    s = So()

    try:
        _socket = s.sock.connect_ex((network_address, 8000))

        if _socket == 0:
            Logger.info('Found online at {}'.format(network_address))

            responded_msgs = s.sock.recv(2048)
            scanned_online_urls[network_address] = str(responded_msgs.decode())

            Logger.info('Device on address {} responded with message {}'.format(network_address,
                                                                                str(responded_msgs.decode())))
            s.sock.close()

        else:
            Logger.info('{} responded {}'.format(network_address, _socket))

    finally:
        s.sock.close()
        Logger.info(
            'Current :{} Exiting for {} and closing {}'.format(threading.currentThread().getName(), _subnet, s))


def start_scanning(*args):
    for _subnet_in in range(3, 20):
        t2 = threading.Thread(target=scan_network_for_single_connection, args=(_subnet_in,))
        t2.start()


"""SCAN"""

"""API REQUESTS"""

hashed_dic_shows = OrderedDict()
hashed_dic_show = OrderedDict()
hashed_dic_movie = OrderedDict()
hashed_dic_movies = OrderedDict()
hashed_dic_search = OrderedDict()
scanned_online_urls = OrderedDict()
chosen_scanned_url = ''


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


class api:

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
            App.get_running_app().conn_error_popup.open()
            Logger.warning('NoConnection: duo to {}'.format(e))

    def get_search_by_id(self):
        self._url_prepared = self.short_url + self.query['_id']
        try:
            return requests.get(self._url_prepared)
        except Exception as e:
            App.get_running_app().conn_error_popup.open()
            Logger.warning('NoConnection: duo to {}'.format(e))

    def get_pages(self):
        try:
            return requests.get(self.url)
        except Exception as e:
            App.get_running_app().conn_error_popup.open()
            Logger.warning('NoConnection: duo to {}'.format(e))


class Movies(api):
    def __init__(self, page=None, sort=None, order=None, keywords=None, _id=None, genre=None, **kwargs):

        self.url = self._url('/movies')
        self.short_url = self._url('/movie/')
        self.query = {}

        if page:
            self.query['page'] = page
            Logger.info('page {}'.format(page))
        if sort:
            self.query['sort'] = str(sort).replace(' ', '%20')
            Logger.info('sort {}'.format(str(sort).replace(' ', '%20')))
        if order:
            self.query['order'] = order
            Logger.info('order {} '.format(order))
        if _id:
            self.query['_id'] = _id
            Logger.info('_id {}'.format(_id))
        if genre:
            self.query['genre'] = genre
            Logger.info('genre {}'.format(genre))
        if keywords:
            self.query['keywords'] = str(keywords).replace(' ', '%20')
            Logger.info('keywords {}'.format(str(keywords).replace(' ', '%20')))


class Shows(api):
    def __init__(self, page=None, sort=None, order=None, keywords=None, _id=None, genre=None, **kwargs):

        self.url = self._url('/shows')
        self.short_url = self._url('/show/')
        self.query = {}

        if page:
            self.query['page'] = page
            Logger.info('page {}'.format(page))
        if sort:
            self.query['sort'] = str(sort).replace(' ', '%20')
            Logger.info('sort {}'.format(str(sort).replace(' ', '%20')))
        if order:
            self.query['order'] = order
            Logger.info('order {} '.format(order))
        if _id:
            self.query['_id'] = _id
            Logger.info('_id {}'.format(_id))
        if genre:
            self.query['genre'] = genre
            Logger.info('genre {}'.format(genre))
        if keywords:
            self.query['keywords'] = str(keywords).replace(' ', '%20')
            Logger.info('keywords {}'.format(str(keywords).replace(' ', '%20')))


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
    Logger.info('HashItem: json {}'.format(__json_in))

    if method_flag:
        Logger.info('going for multi flag {}'.format(method_flag))
        for i in __json_in:

            hashed = hash_item_m(i['_id'])
            __json_hashed_out[hashed] = i
    else:
        Logger.info('going for multi flag {}'.format(method_flag))
        hashed = hash_item_m(__json_in['_id'])
        __json_hashed_out[hashed] = __json_in

    return __json_hashed_out


def populate_hashed_json_dic(__json_hashed_in, to_dic):
    to_dic.clear()

    for i in __json_hashed_in:
        to_dic[i] = __json_hashed_in[i]
    Logger.info('populated dic')


def api_request_controler(_api_call_response):

    if 'keywords' in _api_call_response.url:
        populate_hashed_json_dic(hash_item(_api_call_response.json(), True), hashed_dic_search)

    else:
        try:
            if Shows().short_url in _api_call_response.url:
                populate_hashed_json_dic(hash_item(_api_call_response.json(), False), hashed_dic_show)
        except Exception as e:
            Logger.info('GetApi: Show failed duo to : {}'.format(e))
            pass
        try:
            if Movies().short_url in _api_call_response.url:
                populate_hashed_json_dic(hash_item(_api_call_response.json(), False), hashed_dic_movie)
        except Exception as e:
            Logger.info('GetApi: Movie failed duo to : {}'.format(e))
            pass
        try:
            if Movies().url in _api_call_response.url:
                populate_hashed_json_dic(hash_item(_api_call_response.json(), True), hashed_dic_movies)
        except Exception as e:
            Logger.info('GetApi: Movies failed duo to : {}'.format(e))
            pass
        try:
            if Shows().url in _api_call_response.url:
                populate_hashed_json_dic(hash_item(_api_call_response.json(), True), hashed_dic_shows)
        except Exception as e:
            Logger.info('GetApi: Shows failed duo to : {}'.format(e))
            pass


def get_api(_api_call):
    try:
        api_request_handler(_api_call)
        api_request_controler(_api_call)
    except Exception as e:
        Logger.info('GetApi: failed duo to : {}'.format(e))
        raise Exception


"""API REQUESTS"""


"""CONNECTOR"""


class Connector:
    url = ''

    def __init__(self, **kwargs):
        Logger.info('Connector: Initialized {}'.format(self))

        if self.url:
            self.host = self.url
        else:
            self.host = None
        self.port = 8000
        self.server_state = True
        self.connects(self.host, self.port)

    def connects(self, host, port, *args):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(3)
            self.sock.connect((host,port))
            self.receive()
            Logger.info('Connected to host {}'.format(host))

        except Exception as e :
            Logger.info('No connection to device due to {}'.format(e))

            self.server_state = False
            pass

    def mysend(self, msg, *args):
        if self.server_state:
            try:
                self.sock.send(msg.encode())
                self.receive()
            except:
                pass
        else:
            Logger.info('No connection to device')

    def receive(self, *args):
        responded_msg = self.sock.recv(2048)
        # Logger.info(responded_msg.decode())
        if not len(responded_msg.decode()):
            Logger.info('device responded with no message')

            self.server_state = False
            Logger.info('device state false')

            try:
                self.sock.close()
            except OSError:
                Logger.info('not able to close')

                pass
            self.connects(self.host, self.port)

        else:
            self.server_state = True
            Logger.info('device connection sucess')


"""CONNECTOR"""


def start_loade(instance, *args):
    App.get_running_app().loader_overlay.open()
    Logger.info('start loader for {}'.format(instance))


def stop_loade(instance, *args):
    App.get_running_app().loader_overlay.dismiss()
    Logger.info('stop loader for {}'.format(instance))


def busy_loading_overlay(entry, finish):
    Clock.schedule_once(start_loade, entry)
    Clock.schedule_once(stop_loade, finish)


"""APP"""


class MoviesEpSingleTor(BoxLayout):

    def __init__(self, _torrent_single, _torrent_single_magnet, movies_connector,  **kwargs):
        super(MoviesEpSingleTor, self).__init__(**kwargs)
        Logger.info('MoviesViewMainSingle: MovieEpSingleTor Initialized {}'.format(self))

        self.wtf = movies_connector

        self._torrent_quality = str(_torrent_single)
        self._torrent_quality = self._torrent_quality.encode('utf-8')
        self.ids.tor_quality_label.text = self._torrent_quality
        self._magnet_link = str(_torrent_single_magnet)
        self._magnet_link = self._magnet_link.encode('utf-8')
        self.play = 'play/{}'.format(self._magnet_link)
        self.download = 'down/{}'.format(self._magnet_link)

    def play_torrent(self, *args):
        self.wtf.mysend(self.play)
        Logger.warning('Trying: should be message "{}" '.format(self.play))

    def download_torrent(self, *args):
        self.wtf.mysend(self.download)
        Logger.warning('Trying: should be message "{}" '.format(self.download))


class MoviesEpTor(BoxLayout):

    def __init__(self, _torrents_list, movies_connector, **kwargs):
        super(MoviesEpTor, self).__init__(**kwargs)
        Logger.info('MoviesViewMainSingle: MoviesEpTor Initialized {}'.format(self))

        Logger.info('MoviesViewMainSingle: MoviesEpTor torrents list {}'.format(_torrents_list))

        for _torrent in _torrents_list:
            Logger.info('MoviesViewMainSingle: MoviesEpTor torrent {}'.format(_torrent))

            _mag_link = _torrents_list[_torrent]['url']
            self.add_widget(MoviesEpSingleTor(_torrent, _mag_link, movies_connector))


class MoviesViewMainSingleTop(BoxLayout):

    def __init__(self, mo_year, mo_synopsis, mo_runtime, mo_image, **kwargs):
        super(MoviesViewMainSingleTop, self).__init__(**kwargs)
        Logger.info('MoviesViewMainSingleTop: Initialized {}'.format(self))

        self._mo_year = mo_year
        self._mo_synopsis = mo_synopsis
        self._mo_runtime = mo_runtime
        self._mo_image = mo_image

        self.ids.movies_view_main_single_top_im_holder_IM.source = self._mo_image
        self.ids.movies_view_main_single_top_other_YE.text = 'Year {}'.format(str(self._mo_year))
        self.ids.movies_view_main_single_top_other_RU.text = 'Runtime {}'.format(str(self._mo_runtime))
        self.ids.movies_view_main_single_top_other_DE.text = self._mo_synopsis


class MoviesViewMainSingle(Screen):

    def __init__(self, movie_id, **kwargs):
        super(MoviesViewMainSingle, self).__init__(**kwargs)
        self.movies_single_connector = Connector()

        self.movie_id = movie_id
        self.name = 'mvms'
        self.movies_main_single_screen_instance = self

        Logger.info('MoviesViewMainSingle: Initialized {}'.format(self.name))

        for _single_movie_item_in_dic in hashed_dic_movie:

            Logger.info('Movie level >>>>>')

            Logger.info(' Movie title {}'.format(hashed_dic_movie[_single_movie_item_in_dic]['title']))
            _movie_t = str(hashed_dic_movie[_single_movie_item_in_dic]['title'])
            _movie_t = _movie_t.encode('utf-8')
            self.ids.movies_view_main_single_nav_title_t.text = _movie_t

            Logger.info(' Movie year {}'.format(hashed_dic_movie[_single_movie_item_in_dic]['year']))
            _movie_y = str(hashed_dic_movie[_single_movie_item_in_dic]['year'])
            _movie_y = _movie_y.encode('utf-8')

            # Logger.info(' Movie synopsis {}'.format(hashed_dic_movie[_single_movie_item_in_dic]['synopsis']))
            _movie_s = hashed_dic_movie[_single_movie_item_in_dic]['synopsis']
            _movie_s = _movie_s.encode('utf-8')

            Logger.info(' Movie runtime {}'.format(hashed_dic_movie[_single_movie_item_in_dic]['runtime']))
            _movie_r = str(hashed_dic_movie[_single_movie_item_in_dic]['runtime'])
            _movie_r = _movie_r.encode('utf-8')

            try:
                Logger.info(' Movie image {}'.format(hashed_dic_movie[_single_movie_item_in_dic]['images']['poster']))
                _movie_im = str(hashed_dic_movie[_single_movie_item_in_dic]['images']['poster'])
                _movie_im = _movie_im.encode('utf-8')
            except KeyError:
                Logger.info(' Movie image fallback{}')
                _movie_im = './images/logo.png'
                pass

            Logger.info(
                ' Movie number of torrents {}'.format(len(hashed_dic_movie[_single_movie_item_in_dic]['torrents']['en'])))
            self.movie_torr_num = len(hashed_dic_movie[_single_movie_item_in_dic]['torrents']['en'])

            self.ids.movies_view_main_single_container.add_widget(
                MoviesViewMainSingleTop(_movie_y, _movie_s, _movie_r, _movie_im))

            self.ids.movies_view_main_single_container_se.add_widget(MoviesEpTor(hashed_dic_movie[_single_movie_item_in_dic]['torrents']['en'], self.movies_single_connector))

    def go_back_to_movies(self,*args):
        if 'latest view main screen' in self.manager.screen_names:
            Logger.info('back from latest')

            self.manager.current = 'latest view main screen'
        elif 'search view main screen' in self.manager.screen_names:
            Logger.info('back from search')

            self.manager.current = 'search view main screen'
        else:
            Logger.info('back from movies')

            self.manager.current = 'movies view main screen'

        self.manager.remove_widget(self.movies_main_single_screen_instance)


class MoviesViewMain(Screen):

    def __init__(self, **kwargs):
        super(MoviesViewMain, self).__init__(**kwargs)
        self.name = 'movies view main screen'
        Logger.info('MoviesViewMain: Initialized {}'.format(self.name))

        movies_layout = GridLayout(cols=3, padding=17, spacing=15,
                            size_hint=(None, None), width=ViewControl.width_x - 30)

        movies_layout.bind(minimum_height=movies_layout.setter('height'))

        movies_scroll_list = ScrollView(size_hint=(None, None), size=(ViewControl.width_x - 20, ViewControl.height_x * 0.8),
                          pos_hint={'center_x': 0.5, 'center_y': 1}, do_scroll_x=False)

        movies_scroll_list.add_widget(movies_layout)
        self.ids.movies_view_main_container.add_widget(movies_scroll_list)

        for _movie in hashed_dic_movies:
            self._items = Item(hashed_dic_movies[_movie]['_id'])
            self._items.size = ((Window.size[0] / 3) - 30, (Window.size[1] / 2) - 300)
            try:
                self._items.add_widget(AsyncImage(source=hashed_dic_movies[_movie]['images']['poster'], nocache=True, on_error=self.async_image_error_load))
            except:
                Logger.info('No image setting default')

                self._items.add_widget(Image(source='images/logo.png'))
                pass

            self._items.add_widget(Button(text=hashed_dic_movies[_movie]['title'], size_hint_y=.1, text_size=(((Window.size[0] / 3)-45), None), shorten_from='right', halign='center', shorten=True, on_press=partial(self.change_to_movies_single, self._items.megs)))

            movies_layout.add_widget(self._items)

    def async_image_error_load(self, instance, *args):
        Logger.info('MoviesViewMain: Async image failed {}'.format(instance))

        instance.source = './images/logo.png'

    def change_to_movies_single(instance, __movie_id, *args):
        Logger.info('MoviesViewMain: change_to_movies_single {}'.format(__movie_id))

        Clock.schedule_once(partial(start_loade, instance), -1)
        Clock.schedule_once(partial(instance.add_scmm, __movie_id), 0.5)
        Clock.schedule_once(partial(stop_loade, instance), 3)

    def add_scmm(self, __s_id, *args):
        get_api(Movies(_id=__s_id).get_search_by_id())
        self.manager.add_widget(MoviesViewMainSingle(__s_id))
        self.manager.current = 'mvms'


class ScMaMovies(ScreenManager):

    def __init__(self, **kwargs):
        super(ScMaMovies, self).__init__(**kwargs)
        Logger.info('ScMaMovies: Initialized {}'.format(self))

        if MoviesView.skipper:
            Clock.schedule_once(self.add_scmm, 0)
        else:

            Clock.schedule_once(partial(start_loade, self), -1)
            Clock.schedule_once(self.add_scmm, 0.5)
            Clock.schedule_once(partial(stop_loade, self), 3)

    def add_scmm(self, *args):
        self.add_widget(MoviesViewMain())
        MoviesView.skipper = False


class PaginationButton(Button):
    def __init__(self, set_as_text, **kwargs):
        super(PaginationButton, self).__init__(**kwargs)
        self.text = set_as_text


class MoviesView(Screen):
    skipper = BooleanProperty(True)
    _filter_order = StringProperty(None)
    _filter_sort = StringProperty(None)
    _filter_genre = StringProperty(None)
    _filter_type = StringProperty(None)

    def __init__(self, **kwargs):
        super(MoviesView, self).__init__(**kwargs)
        Logger.info('MoviesView: Initialized {}'.format(self))

        self.movies_paginator = GridLayout(rows=1, cols=50, padding=5, spacing=5, size_hint=(None, None))
        self.movies_paginator.bind(minimum_width=self.movies_paginator.setter('width'))

        for i in range(1, 50):
            self.btn_m_p = PaginationButton(str(i))
            self.btn_m_p.bind(on_press=lambda instance: self.m_paginator_buton_call(instance))
            self.movies_paginator.add_widget(self.btn_m_p)
        self.scroll = ScrollView(size_hint=(1, 1), do_scroll_x=True, do_scroll_y=False)

        self.scroll.add_widget(self.movies_paginator)
        self.ids.movies_pag_holder.add_widget(self.scroll)

        self.ids.mov_view_holder.add_widget(ScMaMovies())

    def m_paginator_buton_call(self, paginator_button_instance, *args):

        for pag_bu in self.movies_paginator.children:
            pag_bu.background_color = [1, 1, 1, 1]

        self.ids.mov_view_holder.remove_widget(self.ids.mov_view_holder.children[0])

        try:
            paginator_button_instance.background_color = get_color_from_hex('#ffa500')

            x_sort = self._filter_sort
            x_order = self._filter_order
            if x_order is None:
                Logger.info('MoviesView: _filter_order setting to default cause is  {}'.format(x_order))

                x_order = '-1'

            if x_sort is None:
                Logger.info('MoviesView: _filter_sort setting to default cause is  {}'.format(x_sort))

                x_sort = 'last added'

            Logger.info('MoviesView: _filter_order  is  {}'.format(self._filter_order))
            Logger.info('MoviesView: _filter_sort  is  {}'.format(self._filter_sort))
            Logger.info('MoviesView: _filter_genre  is  {}'.format(self._filter_genre))

            get_api(Movies(page=paginator_button_instance.text, order=x_order, sort=x_sort, genre=self._filter_genre).get_search())

            self.ids.mov_view_holder.add_widget(ScMaMovies())
        except Exception as e:
            Logger.warning('MoviesView: fail due to  {}'.format(e))

            App.get_running_app().conn_error_popup.open()
            pass


class Item(BoxLayout):
    def __init__(self, sname, **kwargs):
        super(Item, self).__init__(**kwargs)
        Logger.info('Item: Initialized {}'.format(self))

        self.megs = sname
        Logger.info('Item: sname {}'.format(self.megs))


class SeriesViewMainSingleTop(BoxLayout):
    def __init__(self, sh_year, sh_synopsis, sh_runtime, sh_image, sh_status, **kwargs):
        super(SeriesViewMainSingleTop, self).__init__(**kwargs)
        Logger.info('SeriesViewMainSingleTop: Initialized {}'.format(self))

        self._sh_year = sh_year
        self._sh_synopsis = sh_synopsis
        self._sh_runtime = sh_runtime
        self._sh_image = sh_image
        self._sh_status = sh_status

        self.ids.series_view_main_single_top_im_holder_IM.source = self._sh_image
        self.ids.series_view_main_single_top_other_YE.text = 'Year {}'.format(str(self._sh_year))
        self.ids.series_view_main_single_top_other_RU.text = 'Runtime {}'.format(str(self._sh_runtime))
        self.ids.series_view_main_single_top_other_ST.text = 'Status : {}'.format(str(self._sh_status))
        self.ids.series_view_main_single_top_other_DE.text = self._sh_synopsis


class ShowEpSingleTor(BoxLayout):
    def __init__(self, _torrent_single, _torrent_single_magnet, series_connector,  **kwargs):
        super(ShowEpSingleTor, self).__init__(**kwargs)
        Logger.info('SeriesViewMainSingle: ShowEpSingleTor Initialized {}'.format(self))
        self.wtf = series_connector

        self._torrent_quality = str(_torrent_single)
        self._torrent_quality = self._torrent_quality.encode('utf-8')
        self.ids.tor_quality_label.text = self._torrent_quality
        self._magnet_link = str(_torrent_single_magnet)
        self._magnet_link = self._magnet_link.encode('utf-8')
        self.play = 'play/{}'.format(self._magnet_link)
        self.download = 'down/{}'.format(self._magnet_link)

    def play_torrent(self, *args):
        self.wtf.mysend(self.play)
        Logger.warning('Trying: should be message "{}" '.format(self.play))

    def download_torrent(self, *args):
        self.wtf.mysend(self.download)
        Logger.warning('Trying: should be message "{}" '.format(self.download))


class ShowEpTor(BoxLayout):
    def __init__(self, _torrents_list, series_connector, **kwargs):
        super(ShowEpTor, self).__init__(**kwargs)
        Logger.info('SeriesViewMainSingle: ShowEpTor Initialized {}'.format(self))

        Logger.info('SeriesViewMainSingle: ShowEpTor torrents list {}'.format(_torrents_list))

        for _torrent in _torrents_list:
            Logger.info('SeriesViewMainSingle: ShowEpTor torrent {}'.format(_torrent))

            try:
                _mag_link = _torrents_list[_torrent]['url']
                self.add_widget(ShowEpSingleTor(_torrent, _mag_link, series_connector))
            except TypeError:
                Logger.info('SeriesViewMainSingle: ShowEpTor torrent missing {}'.format(_torrent))
                pass


class ShowEpSyn(BoxLayout):
    def __init__(self, _show_episode_synopsis_text_in, **kwargs):
        super(ShowEpSyn, self).__init__(**kwargs)
        Logger.info('SeriesViewMainSingle: ShowEpSyn Initialized {}'.format(self))

        self._show_episode_synopsis_text_in = _show_episode_synopsis_text_in
        self.ids.show_episode_syn.text = self._show_episode_synopsis_text_in


class SeriesViewMainSingle(Screen):
    def __init__(self, series_id, **kwargs):
        super(SeriesViewMainSingle, self).__init__(**kwargs)
        self.series_single_connector = Connector()

        self.series_id = series_id
        self.name = 'svms'
        self.series_main_singe_screen_instance = self

        Logger.info('SeriesViewMainSingle: Initialized {}'.format(self.name))

        self.buffe = []

        for _single_show_item_in_dic in hashed_dic_show:
            for show_node in hashed_dic_show[_single_show_item_in_dic]:

                if show_node == 'episodes':
                    self.episode_count = int(len(hashed_dic_show[_single_show_item_in_dic]['episodes']))
                    self.accord_height = dp((1 * 44) + 340)

                    self._single_show_accordion = Accordion(orientation='vertical', height=self.accord_height, size_hint_y=None, min_space=dp(44))

                    self._single_show_accordion.id = 'testAccordian'

                    self.g_scroll_list = ScrollView(size_hint=(None, None),
                                                    size=(ViewControl.width_x - 40, ViewControl.height_x * 0.4),on_scroll_move=self.sch_lazy,pos_hint={'center_x': 0.5, 'center_y': 0.5})

                    self.ids.series_view_main_single_container_se.add_widget(self.g_scroll_list)
                    self.g_scroll_list.add_widget(self._single_show_accordion)

                    Logger.info('Show level >>>>>')

                    Logger.info(' Show title {}'.format(hashed_dic_show[_single_show_item_in_dic]['title']))
                    _show_t = str(hashed_dic_show[_single_show_item_in_dic]['title'])
                    _show_t = _show_t.encode('utf-8')
                    self.ids.series_view_main_single_nav_title_t.text = _show_t

                    Logger.info(' Show year {}'.format(hashed_dic_show[_single_show_item_in_dic]['year']))
                    _show_y = str(hashed_dic_show[_single_show_item_in_dic]['year'])
                    _show_y = _show_y.encode('utf-8')

                    # Logger.info(' Show synopsis {}'.format(hashed_dic_show[_single_show_item_in_dic]['synopsis']))
                    _show_s = hashed_dic_show[_single_show_item_in_dic]['synopsis']
                    _show_s = _show_s.encode('utf-8')

                    Logger.info(' Show runtime {}'.format(hashed_dic_show[_single_show_item_in_dic]['runtime']))
                    _show_r = str(hashed_dic_show[_single_show_item_in_dic]['runtime'])
                    _show_r = _show_r.encode('utf-8')

                    try:
                        Logger.info(' Show image {}'.format(hashed_dic_show[_single_show_item_in_dic]['images']['poster']))
                        _show_im = str(hashed_dic_show[_single_show_item_in_dic]['images']['poster'])
                        _show_im = _show_im.encode('utf-8')
                    except KeyError:
                        Logger.info(' Show image fallback{}')
                        _show_im = './images/logo.png'
                        pass

                    Logger.info(' Show status {}'.format(hashed_dic_show[_single_show_item_in_dic]['status']))
                    _show_st = str(hashed_dic_show[_single_show_item_in_dic]['status'])
                    _show_st = _show_st.encode('utf-8')

                    Logger.info(' Show number of episodes {}'.format(len(hashed_dic_show[_single_show_item_in_dic]['episodes'])))
                    self._ep_num = len(hashed_dic_show[_single_show_item_in_dic]['episodes'])

                    self.ids.series_view_main_single_container.add_widget(
                        SeriesViewMainSingleTop(_show_y, _show_s, _show_r, _show_im, _show_st))
                    lok = 0
                    for _episode_node in hashed_dic_show[_single_show_item_in_dic][show_node]:
                        lok += 1
                        acc_item = AccordionItem(collapse=True, orientation='vertical',background_normal='./images/filter_list_i.png',
    background_selected='./images/filter_list_i.png')

                        acc_item.container.orientation = 'vertical'
                        Logger.info('Episode level >>>>>')
                        # Logger.info(z)
                        try:
                            Logger.info('Episode title {}'.format(_episode_node['title']))
                        except UnicodeEncodeError:
                            pass

                        if _episode_node['title']:
                            ti = _episode_node['title'].encode('utf-8')
                        else:
                            ti = ''

                        Logger.info('Episode overview')
                        if _episode_node['overview']:
                            _show_episode_over = _episode_node['overview']
                            _show_episode_over = _show_episode_over.encode('utf-8')
                            Logger.info('Episode overview {}'.format(_show_episode_over))
                        else:
                            _show_episode_over = ''

                        Logger.info('Episode episode number {}'.format(_episode_node['episode']))
                        _show_episode = str(_episode_node['episode'])
                        _show_episode = _show_episode.encode('utf-8')

                        Logger.info('Episode season number {}'.format(_episode_node['season']))
                        _show_season = str(_episode_node['season'])
                        _show_season = _show_season.encode('utf-8')

                        acc_item.title = '{} {} {}'.format(ti, _show_season, _show_episode)

                        _show_accordion_item_container_synopsis = ShowEpSyn(str(_show_episode_over))

                        acc_item.container.add_widget(_show_accordion_item_container_synopsis)

                        acc_item.container.add_widget(ShowEpTor(_episode_node['torrents'], self.series_single_connector))

                        # self._single_show_accordion.add_widget(acc_item)
                        self.buffe.append(acc_item)
                        if lok < 5:
                            self.lazyy()

    def sch_lazy(self, *args):
        scroller = args[0].scroll_y
        if 0.09 < scroller < 0.2:
            Clock.schedule_once(self.lazyy, .3)

    def lazyy(instance, *args):
        if instance.buffe:
            instance._single_show_accordion.height += dp(44)
            item_from_buff = instance.buffe[0]

            instance._single_show_accordion.add_widget(item_from_buff)
            instance.buffe.remove(item_from_buff)

    def go_back_to_series(self,*args):

        if 'latest view main screen' in self.manager.screen_names:
            Logger.info('back from latest')
            self.manager.current = 'latest view main screen'
        elif 'search view main screen' in self.manager.screen_names:
            Logger.info('back from search')
            self.manager.current = 'search view main screen'
        else:
            Logger.info('back from series')
            self.manager.current = 'series view main screen'

        self.manager.remove_widget(self.series_main_singe_screen_instance)


class SeriesViewMain(Screen):
    def __init__(self, **kwargs):
        super(SeriesViewMain, self).__init__(**kwargs)
        self.name = 'series view main screen'
        Logger.info('SeriesViewMain: Initialized {}'.format(self.name))

        series_layout = GridLayout(cols=3, padding=17, spacing=15,
                                   size_hint=(None, None), width=ViewControl.width_x - 30)
        series_layout.bind(minimum_height=series_layout.setter('height'))

        series_scroll_list = ScrollView(size_hint=(None, None),
                                        size=(ViewControl.width_x - 20, ViewControl.height_x * 0.8),
                                        pos_hint={'center_x': 0.5, 'center_y': 1}, do_scroll_x=False)
        series_scroll_list.add_widget(series_layout)
        self.ids.series_view_main_container.add_widget(series_scroll_list)

        for _show in hashed_dic_shows:
            self._items = Item(hashed_dic_shows[_show]['_id'])
            self._items.size = ((Window.size[0] / 3) - 30, (Window.size[1] / 2) - 300)

            try:
                self._items.add_widget(AsyncImage(source=hashed_dic_shows[_show]['images']['poster'], nocache=True, on_error=self.async_image_error_load))
            except Exception:
                Logger.info('No image setting default')

                self._items.add_widget(Image(source='/images/logo.png'))
                pass

            self._items.add_widget(Button(text=hashed_dic_shows[_show]['title'], size_hint_y=.1, text_size=(((Window.size[0] / 3)-45), None), shorten_from='right', halign='center', shorten=True, on_press=partial(self.change_to_series_single, self._items.megs)))

            series_layout.add_widget(self._items)

    def async_image_error_load(self, instance, *args):
        Logger.info('SeriesViewMain: Async image failed {}'.format(instance))

        instance.source = './images/logo.png'

    def change_to_series_single(instance, __show_id, *args):
        Logger.info('SeriesViewMain: change_to_series_single {}'.format(__show_id))

        Clock.schedule_once(partial(start_loade, instance), -1)
        Clock.schedule_once(partial(instance.add_scms, __show_id), 2)
        Clock.schedule_once(partial(stop_loade, instance), 4)

    def add_scms(self, __s_id, *args):
        get_api(Shows(_id=__s_id).get_search_by_id())

        self.manager.add_widget(SeriesViewMainSingle(__s_id))
        self.manager.current = 'svms'


class ScMaSeries(ScreenManager):
    def __init__(self, **kwargs):
        super(ScMaSeries, self).__init__(**kwargs)
        Logger.info('ScMaSeries: Initialized {}'.format(self))

        if SeriesView.skipper:
            Clock.schedule_once(self.add_scms, 0)
        else:

            Clock.schedule_once(partial(start_loade, self), -1)
            Clock.schedule_once(self.add_scms, 0.5)
            Clock.schedule_once(partial(stop_loade, self), 4)

    def add_scms(self, *args):
        self.add_widget(SeriesViewMain())
        SeriesView.skipper = False


class SeriesView(Screen):
    skipper = BooleanProperty(True)
    _filter_order = StringProperty(None)
    _filter_sort = StringProperty(None)
    _filter_genre = StringProperty(None)
    _filter_type = StringProperty(None)

    def __init__(self, **kwargs):
        super(SeriesView, self).__init__(**kwargs)
        Logger.info('SeriesView: Initialized {}'.format(self))
        Logger.info('This is window size {}'.format(Window.size))
        Logger.info('This is container size {}'.format(self.size))

        self.series_paginator = GridLayout(rows=1, cols=50, padding=5, spacing=5, size_hint=(None, None))
        self.series_paginator.bind(minimum_width=self.series_paginator.setter('width'))

        for i in range(1, 50):
            self.btn_s_p = PaginationButton(str(i))
            self.btn_s_p.bind(on_press=lambda instance: self.s_paginator_buton_call(instance))
            self.series_paginator.add_widget(self.btn_s_p)

        self.scroll = ScrollView(size_hint=(1, 1), do_scroll_x=True, do_scroll_y=False)

        self.scroll.add_widget(self.series_paginator)
        self.ids.series_pag_holder.add_widget(self.scroll)

        self.ids.ser_view_holder.add_widget(ScMaSeries())

    def s_paginator_buton_call(self, paginator_button_instance, *args):

        for pag_bu in self.series_paginator.children:
            pag_bu.background_color = [1, 1, 1, 1]

        self.ids.ser_view_holder.remove_widget(self.ids.ser_view_holder.children[0])

        try:
            paginator_button_instance.background_color = get_color_from_hex('#ffa500')
            y_sort = self._filter_sort
            y_order = self._filter_order
            if y_order is None:
                Logger.info('SeriesView: _filter_order setting to default cause is  {}'.format(y_order))

                y_order = '-1'
            if y_sort is None:
                Logger.info('SeriesView: _filter_sort setting to default cause is  {}'.format(y_sort))

                y_sort = 'updated'

            Logger.info('SeriesView: _filter_order  is  {}'.format(self._filter_order))
            Logger.info('SeriesView: _filter_sort  is  {}'.format(self._filter_sort))
            Logger.info('SeriesView: _filter_genre  is  {}'.format(self._filter_genre))
            get_api(Shows(page=paginator_button_instance.text, order=y_order, sort=y_sort, genre=self._filter_genre).get_search())

            self.ids.ser_view_holder.add_widget(ScMaSeries())
        except Exception as e:
            Logger.warning('SeriesView: fail due to  {}'.format(e))

            App.get_running_app().conn_error_popup.open()
            pass


class SearchViewMain(Screen):

    def __init__(self, search_type, **kwargs):
        super(SearchViewMain, self).__init__(**kwargs)
        self.name = 'search view main screen'
        Logger.info('SearchViewMain: Initialized {}'.format(self.name))

        self.typ = search_type
        self.ids.search_typee.text = self.typ

        """SHOWS SEARCH"""
        if self.typ == 'Shows':

            search_series_layout = GridLayout(cols=3, padding=20, spacing=15,
                                       size_hint=(None, None), width=ViewControl.width_x - 30)

            search_series_layout.bind(minimum_height=search_series_layout.setter('height'))

            search_series_scroll_list = ScrollView(size_hint=(None, None),
                                            size=(ViewControl.width_x - 20, ViewControl.height_x * 0.8),
                                            pos_hint={'center_x': 0.5, 'center_y': .5}, do_scroll_x=False)

            search_series_scroll_list.add_widget(search_series_layout)
            self.ids.search_view_main_container_holder.add_widget(search_series_scroll_list)

            for _search_item_show in hashed_dic_search:

                self._items_search_s = Item(hashed_dic_search[_search_item_show]['_id'])
                self._items_search_s.size = ((Window.size[0] / 3) - 30, (Window.size[1] / 2) - 300)

                try:
                    self._items_search_s.add_widget(AsyncImage(source=hashed_dic_search[_search_item_show]['images']['poster'], nocache=True, on_error=self.async_image_error_load))
                except Exception:
                    Logger.info('No image setting default')

                    self._items_search_s.add_widget(Image(source='/images/logo.png'))
                    pass

                self._items_search_s.add_widget(Button(text=hashed_dic_search[_search_item_show]['title'], size_hint_y=.1, text_size=(((Window.size[0] / 3)-45), None), shorten_from='right', halign='center', shorten=True, on_press=partial(self.change_to_series_single, self._items_search_s.megs)))

                search_series_layout.add_widget(self._items_search_s)

            """MOVIES SEARCH"""
        else:
            search_movies_layout = GridLayout(cols=3, padding=20, spacing=15,
                                       size_hint=(None, None), width=ViewControl.width_x - 30)

            search_movies_layout.bind(minimum_height=search_movies_layout.setter('height'))

            search_movies_scroll_list = ScrollView(size_hint=(None, None), size=(ViewControl.width_x - 20, ViewControl.height_x * 0.8),
                                            pos_hint={'center_x': 0.5, 'center_y': 0.5}, do_scroll_x=False)

            search_movies_scroll_list.add_widget(search_movies_layout)
            self.ids.search_view_main_container_holder.add_widget(search_movies_scroll_list)

            for _search_item_movie in hashed_dic_search:
                self._items_search_m = Item(hashed_dic_search[_search_item_movie]['_id'])
                self._items_search_m.size = ((Window.size[0] / 3) - 30, (Window.size[1] / 2) - 300)
                try:
                    self._items_search_m.add_widget(AsyncImage(source=hashed_dic_search[_search_item_movie]['images']['poster'], nocache=True,
                                                      on_error=self.async_image_error_load))
                except Exception:
                    Logger.info('No image setting default')

                    self._items_search_m.add_widget(Image(source='images/logo.png'))
                    pass

                self._items_search_m.add_widget(
                    Button(text=hashed_dic_search[_search_item_movie]['title'], size_hint_y=.1,
                                             text_size=(((Window.size[0] / 3) - 45), None), shorten_from='right',
                                             halign='center', shorten=True, on_press=partial(self.change_to_movies_single, self._items_search_m.megs)))

                search_movies_layout.add_widget(self._items_search_m)

    def async_image_error_load(self, instance, *args):
        Logger.info('SearchViewMain: Async image failed {}'.format(instance))

        instance.source = './images/logo.png'

    def change_to_series_single(instance, __show_id, *args):
        Logger.info('SearchViewMain: change_to_series_single {}'.format(__show_id))

        Clock.schedule_once(partial(start_loade, instance), -1)
        Clock.schedule_once(partial(instance.add_scms, __show_id), 0.5)
        Clock.schedule_once(partial(stop_loade, instance), 4)

    def change_to_movies_single(instance, __movie_id, *args):
        Logger.info('MoviesViewMain: change_to_movies_single {}'.format(__movie_id))

        Clock.schedule_once(partial(start_loade, instance), -1)
        Clock.schedule_once(partial(instance.add_scmm, __movie_id), 0.5)
        Clock.schedule_once(partial(stop_loade, instance), 3)

    def add_scms(self, __s_id, *args):
        get_api(Shows(_id=__s_id).get_search_by_id())

        self.manager.add_widget(SeriesViewMainSingle(__s_id))
        self.manager.current = 'svms'

    def add_scmm(self, __s_id, *args):
        get_api(Movies(_id=__s_id).get_search_by_id())

        self.manager.add_widget(MoviesViewMainSingle(__s_id))
        self.manager.current = 'mvms'


class ScMaSearch(ScreenManager):
    def __init__(self, search_type, **kwargs):
        super(ScMaSearch, self).__init__(**kwargs)
        Logger.info('ScMaSearch: Initialized {}'.format(self))

        self.search_type = search_type
        Logger.info('Search for type {}'.format(self.search_type))

        if SearchView.skipper:
            Clock.schedule_once(self.add_scmsr, 0)
        else:

            Clock.schedule_once(partial(start_loade, self), -1)
            Clock.schedule_once(self.add_scmsr, 0.5)
            Clock.schedule_once(partial(stop_loade, self), 3)

    def add_scmsr(self, *args):
        self.add_widget(SearchViewMain(self.search_type))
        SeriesView.skipper = False


class SearchView(Screen):
    skipper = BooleanProperty(True)
    _search_keywords = StringProperty(None)
    _filter_order = StringProperty(None)
    _filter_sort = StringProperty(None)
    _filter_genre = StringProperty(None)
    _filter_type = StringProperty(None)

    def __init__(self, **kwargs):
        super(SearchView, self).__init__(**kwargs)
        Logger.info('SearchView: Initialized {}'.format(self))
        # Logger.info(self.ids)

        self.ids.search_view_holder.clear_widgets()

    def clear_w(self, *args):
        Logger.info('SearchView: cleaner')

        self.ids.search_view_holder.clear_widgets()

    def on_search_screen_enter(self, *args):
        try:
            if self._filter_type == 'Movies':
                get_api(Movies(page='1', order=self._filter_order, sort=self._filter_sort, genre=self._filter_genre, keywords=self._search_keywords).get_search())
                self.ids.search_view_holder.add_widget(ScMaSearch(self._filter_type))

            elif self._filter_type == 'Shows':
                get_api(Shows(page='1', order=self._filter_order, sort=self._filter_sort, genre=self._filter_genre,
                               keywords=self._search_keywords).get_search())
                self.ids.search_view_holder.add_widget(ScMaSearch(self._filter_type))

            else:
                Logger.info('SearchView: Initialization stopped {}'.format(self._filter_type))

        except Exception as e:
            Logger.warning('SearchView: fail due to {}'.format(e))
            App.get_running_app().conn_error_popup.open()
            pass


class LatestViewMain(Screen):
    def __init__(self, **kwargs):
        super(LatestViewMain, self).__init__(**kwargs)
        self.name = 'latest view main screen'
        Logger.info('LatestViewMain: Initialized {}'.format(self.name))

        """SHOES LATEST"""
        latest_series_layout = GridLayout(cols=3, padding=25, spacing=15,
                                   size_hint=(None, None), width=ViewControl.width_x - 30)
        latest_series_layout.bind(minimum_height=latest_series_layout.setter('height'))

        latest_series_scroll_list = ScrollView(size_hint=(None, None),
                                        size=(ViewControl.width_x - 20, ViewControl.height_x * 0.44),
                                        pos_hint={'center_x': 0.5, 'center_y': .5}, do_scroll_x=False)
        latest_series_scroll_list.add_widget(latest_series_layout)
        self.ids.latest_view_main_shows_container.add_widget(latest_series_scroll_list)

        latest_show_counter = 0
        for _show in hashed_dic_shows:
            if latest_show_counter < 15:
                self._items_latest_s = Item(hashed_dic_shows[_show]['_id'])
                self._items_latest_s.size = ((Window.size[0] / 3) - 30, (Window.size[1] / 2) - 300)

                try:
                    self._items_latest_s.add_widget(AsyncImage(source=hashed_dic_shows[_show]['images']['poster'], nocache=True, on_error=self.async_image_error_load))
                except Exception:
                    Logger.info('No image setting default')

                    self._items_latest_s.add_widget(Image(source='/images/logo.png'))
                    pass

                self._items_latest_s.add_widget(Button(text=hashed_dic_shows[_show]['title'], size_hint_y=.1, text_size=(((Window.size[0] / 3)-45), None), shorten_from='right', halign='center', shorten=True, on_press=partial(self.change_to_series_single, self._items_latest_s.megs)))

                latest_series_layout.add_widget(self._items_latest_s)
                latest_show_counter += 1

        """MOVIES LATEST"""
        latest_movies_layout = GridLayout(cols=3, padding=25, spacing=15,
                                   size_hint=(None, None), width=ViewControl.width_x - 30)

        latest_movies_layout.bind(minimum_height=latest_movies_layout.setter('height'))

        latest_movies_scroll_list = ScrollView(size_hint=(None, None), size=(ViewControl.width_x - 20, ViewControl.height_x * 0.45),
                                        pos_hint={'center_x': 0.5, 'center_y': 0.5}, do_scroll_x=False)

        latest_movies_scroll_list.add_widget(latest_movies_layout)
        self.ids.latest_view_main_movies_container.add_widget(latest_movies_scroll_list)

        latest_movie_counter = 0
        for _movie in hashed_dic_movies:
            if latest_movie_counter < 15:
                self._items_latest_m = Item(hashed_dic_movies[_movie]['_id'])
                self._items_latest_m.size = ((Window.size[0] / 3) - 30, (Window.size[1] / 2) - 300)
                try:
                    self._items_latest_m.add_widget(AsyncImage(source=hashed_dic_movies[_movie]['images']['poster'], nocache=True,
                                                      on_error=self.async_image_error_load))
                except Exception:
                    Logger.info('No image setting default')

                    self._items_latest_m.add_widget(Image(source='images/logo.png'))
                    pass

                self._items_latest_m.add_widget(
                    Button(text=hashed_dic_movies[_movie]['title'], size_hint_y=.1,
                                             text_size=(((Window.size[0] / 3) - 45), None), shorten_from='right',
                                             halign='center', shorten=True, on_press=partial(self.change_to_movies_single, self._items_latest_m.megs)))

                latest_movies_layout.add_widget(self._items_latest_m)
                latest_movie_counter += 1

    def async_image_error_load(self, instance, *args):
        Logger.info('LatestViewMain: Async image failed {}'.format(instance))

        instance.source = './images/logo.png'

    def change_to_series_single(instance, __show_id, *args):
        Logger.info('LatestViewMain: change_to_series_single {}'.format(__show_id))

        Clock.schedule_once(partial(start_loade, instance), -1)
        Clock.schedule_once(partial(instance.add_scms, __show_id), 0.5)
        Clock.schedule_once(partial(stop_loade, instance), 4)

    def change_to_movies_single(instance, __movie_id, *args):
        Logger.info('MoviesViewMain: change_to_movies_single {}'.format(__movie_id))

        Clock.schedule_once(partial(start_loade, instance), -1)
        Clock.schedule_once(partial(instance.add_scmm, __movie_id), 0.5)
        Clock.schedule_once(partial(stop_loade, instance), 3)

    def add_scms(self, __s_id, *args):
        get_api(Shows(_id=__s_id).get_search_by_id())

        self.manager.add_widget(SeriesViewMainSingle(__s_id))
        self.manager.current = 'svms'

    def add_scmm(self, __s_id, *args):
        get_api(Movies(_id=__s_id).get_search_by_id())

        self.manager.add_widget(MoviesViewMainSingle(__s_id))
        self.manager.current = 'mvms'


class ScMaLatest(ScreenManager):

    def __init__(self, **kwargs):
        super(ScMaLatest, self).__init__(**kwargs)
        Logger.info('ScMaLatest: Initialized {}'.format(self))

        if LatestView.skipper:
            Clock.schedule_once(self.add_scms, 0)
        else:

            Clock.schedule_once(partial(start_loade, self), -1)
            Clock.schedule_once(self.add_scms, 0.5)
            Clock.schedule_once(partial(stop_loade, self), 4)

    def add_scms(self, *args):
        self.add_widget(LatestViewMain())
        LatestView.skipper = False


class LatestView(Screen):
    skipper = BooleanProperty(True)
    _filter_order = StringProperty(None)
    _filter_sort = StringProperty(None)
    _filter_genre = StringProperty(None)
    _filter_type = StringProperty(None)

    def __init__(self, **kwargs):
        super(LatestView, self).__init__(**kwargs)
        Logger.info('LatestView: Initialized {}'.format(self))

        self.ids.lat_view_holder.add_widget(ScMaLatest())

    def refresh_on_enter(self, *args):
        Logger.info('LatestView: refresh invoked {}'.format(self))

        if not LatestView.skipper:
            self.ids.lat_view_holder.remove_widget(self.ids.lat_view_holder.children[0])
            Logger.info('LatestView: refresh not skipped {}'.format(self))

            try:
                get_api(Shows(order='-1', sort='updated', genre=self._filter_genre).get_search())
                get_api(Movies(order='-1', sort='last added', genre=self._filter_genre).get_search())
                self.ids.lat_view_holder.add_widget(ScMaLatest())
            except Exception as e:
                Logger.info('LatestView: refresh not skipped failed due to {}'.format(e))

                App.get_running_app().conn_error_popup.open()
                pass
        else:
            Logger.info('LatestView: refresh skipped {}'.format(self))


class MainViewScManager(ScreenManager):
    def __init__(self, **kwargs):
        super(MainViewScManager, self).__init__(**kwargs)
        Logger.info('MainViewScManager: Initialized {}'.format(self))
        self.add_widget(LatestView())
        self.add_widget(SearchView())
        self.add_widget(MoviesView())
        self.add_widget(SeriesView())


class FilterModalView(ModalView):
    def __init__(self, **kwargs):
        super(FilterModalView, self).__init__(**kwargs)
        Logger.info('FilterModalView: Initialized {}'.format(self))
        self.size = (Window.size[0] / 1.5, Window.size[1] / 1.5)
        self.ids.filter_genre.dropdown_cls.max_height = dp(350)

    def close_filter(self, filter_type, filter_genre, filter_order, filter_sort,*args):
        self.filter_type = filter_type
        self.filter_genre = filter_genre
        self.filter_order = filter_order
        self.filter_sort = filter_sort

        if filter_genre == 'Genre':
            self.filter_genre = None
            Logger.info('FilterModalView: set filter_genre to {}'.format(self.filter_genre))

        if filter_order == 'Order':
            self.filter_order = None
            Logger.info('FilterModalView: set filter_order to {}'.format(self.filter_order))

        if filter_sort == 'Sort':
            self.filter_sort = None
            Logger.info('FilterModalView: set filter_sort to {}'.format(self.filter_sort))

        Logger.info('FilterModalView: on dismiss filter_type {}'.format(self.filter_type))
        Logger.info('FilterModalView: on dismiss filter_genre {}'.format(self.filter_genre))
        Logger.info('FilterModalView: on dismiss filter_order {}'.format(self.filter_order))
        Logger.info('FilterModalView: on dismiss filter_sort {}'.format(self.filter_sort))

        MoviesView._filter_type = self.filter_type
        MoviesView._filter_genre = self.filter_genre
        MoviesView._filter_order = self.filter_order
        MoviesView._filter_sort = self.filter_sort
        SeriesView._filter_type = self.filter_type
        SeriesView._filter_genre = self.filter_genre
        SeriesView._filter_order = self.filter_order
        SeriesView._filter_sort = self.filter_sort
        LatestView._filter_type = self.filter_type
        LatestView._filter_genre = self.filter_genre
        LatestView._filter_order = self.filter_order
        LatestView._filter_sort = self.filter_sort
        SearchView._filter_type = self.filter_type
        SearchView._filter_genre = self.filter_genre
        SearchView._filter_order = self.filter_order
        SearchView._filter_sort = self.filter_sort

    def hide_other_accordions(instances, _filter_dropdown_focused):
        for spinner_child in instances.ids.filter_view_container.children[0].children:
            spinner_child.opacity = 0.2
        _filter_dropdown_focused.opacity = 1


class MainView(Screen):
    connection_status_indicator = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(MainView, self).__init__(**kwargs)
        Logger.info('MainView: Initialized {}'.format(self))
        self.view = FilterModalView()

        self.main_scm = MainViewScManager()
        self.ids.screen_m_container.add_widget(self.main_scm)

    def connect_on_enter(self, *args):
        Logger.info('MainView: on enter create connector')

        self.connector = Connector()

        Logger.info('MainView: connection state {}'.format(self.connector.server_state))

        if self.connector.server_state:
            self.update_status_in(self.connector.server_state)
        else:
            self.update_status_in(self.connector.server_state)

        Logger.info('MainView: update connection indicator to {}'.format(self.connector.server_state))

    def open_filter_view(self, *args):
        Logger.info('MainView: open_filter_view invoked')

        self.view.open()

    def set_as_current_screen(self, button_instance, scn, other_but_f, other_but_s, *args):
        Logger.info('MainView: setting active screen {}'.format(scn))

        button_instance.background_normal = "./images/n_b.png"
        other_but_f.background_normal = "./images/n_n.png"
        other_but_s.background_normal = "./images/n_n.png"

        self.main_scm.current = scn

    def set_as_current_screen_search(self, scn, ot_1, ot_2, ot_3, search_in, search_in_container,  *args):
        Logger.info('MainView: setting active screen for search {}'.format(scn))

        ot_1.background_normal = "./images/n_n.png"
        ot_2.background_normal = "./images/n_n.png"
        ot_3.background_normal = "./images/n_n.png"
        if search_in:
            if 'search_view' in str(self.main_scm.current_screen):
                Logger.info('MainView: current screen is  {}'.format(str(self.main_scm.current_screen)))

                self.main_scm.remove_widget(self.main_scm.current_screen)
                Logger.info('MainView: removed old search')

                self.main_scm.add_widget(SearchView())
                self.main_scm.current = scn

            else:
                Logger.info('MainView: navigating to search screen')

                self.main_scm.current = scn

            SearchView._search_keywords = search_in
            search_in_container.text = ''
        else:
            Logger.info('MainView: search input is missing')

            search_in_container.hint_text = 'Missing keywords'
            search_in_container.opacity = .6

    def searchInput_on_focus_effect(self, _search_input_box, _search_input_focus, *args):
        if _search_input_focus:
            _search_input_box.hint_text = ''
            _search_input_box.opacity = 1

        else:
            _search_input_box.opacity = .2

    def navigate_to_settings(self, *args):
        Logger.info('MainView: navigate_to_settings invoked')

        """first time navigation is creating settings screen, if exists just set as current"""

        if 'settings' not in self.manager.screen_names:
            Logger.info('MainView: navigate_to_settings > creating settings view')

            self.manager.switch_to(SettingsView(), transition=FadeTransition())
        else:
            Logger.info('MainView: navigate_to_settings > settings view exists')

            self.manager.current = 'settings'

    def update_status_in(self, status_flagger_flag, *args):
        Logger.info('MainView: Updating connection status invoked')

        if status_flagger_flag:
            self.ids.connection_status_ind_l.source = 'images/on_connection.png'
        else:
            self.ids.connection_status_ind_l.source = 'images/no_connection.png'
    pass


class ScanViewItem(BoxLayout):
    def __init__(self, device_name_for_label, **kwargs):
        super(ScanViewItem, self).__init__(**kwargs)
        Logger.info('ScanViewItem: Initialized {}'.format(self))

        self.dev_name_for_l = device_name_for_label
        self.ids.scan_view_i_name.text = self.dev_name_for_l

    def return_on_active_name(self, scan_item_checkbox_flag, scan_item_checkbox_value,  *args):
        Logger.info('ScanViewItem: return_on_active_name invoked')

        if scan_item_checkbox_flag:
            ScanView.choosen_device = scan_item_checkbox_value
        else:
            ScanView.choosen_device = ''


class ScanView(Screen):
    choosen_device = StringProperty()

    def __init__(self, **kwargs):
        super(ScanView, self).__init__(**kwargs)
        Logger.info('ScanView: Initialized {}'.format(self))

        self._urls_list = scanned_online_urls ## root dictionary with online devices returned from start scanning

        for _urls_list_item in self._urls_list:
            self.formated_dev_name_address = '{}/{}'.format(_urls_list_item, self._urls_list[_urls_list_item])
            self.ids.scanned_devices_list_grid.add_widget(ScanViewItem(self.formated_dev_name_address))

        self.start_service()

    def start_service(self, *args):
        Logger.info('ScanView: start service invoked')

        """get inital latest movies and series, populate shows dictionary populate movies dicionary"""
        try:
            get_api(Shows(order='-1', sort='updated').get_search())
            get_api(Movies(order='-1', sort='last added').get_search())
            Logger.info('ScanView: start service success')

        except Exception as e:
            Logger.info('ScanView: start service fail due to {}'.format(e))

            App.get_running_app().conn_error_popup.open()
            pass

    def set_as_host(self, host_in):
        Logger.info('init scan set_as_host')

        breaker = host_in.find('/')
        prepare_url = host_in[:breaker]
        Connector.url = prepare_url ## set device address for conenctor

    def save_and_go_to_main(self, *args):
        Logger.info('ScanView: Save and go to main screen')

        if self.choosen_device:
            Logger.info('ScanView: setting up device for connection')

            self.set_as_host(self.choosen_device)

        self.manager.switch_to(MainView(), transition=FadeTransition(), duration=1)
        busy_loading_overlay(-0.5, 8)


class SettingsViewItem(BoxLayout):
    def __init__(self, device_name_for_label, **kwargs):
        super(SettingsViewItem, self).__init__(**kwargs)
        Logger.info('SettingsViewItem: Initialized {}'.format(self))

        self.dev_name_for_l = device_name_for_label
        self.ids.settings_view_i_name.text = self.dev_name_for_l

    def return_on_active_name(self, settings_item_checkbox_flag, settings_item_checkbox_value, *args):
        Logger.info('SettingsViewItem: return_on_active_name invoked')

        if settings_item_checkbox_flag:
            SettingsView.choosen_device = settings_item_checkbox_value
        else:
            SettingsView.choosen_device = ''


class SettingsView(Screen):
    choosen_device = StringProperty()

    def __init__(self, **kwargs):
        super(SettingsView, self).__init__(**kwargs)
        Logger.info('SettingsView: Initialized {}'.format(self))

        self.settings_scanned_devices = scanned_online_urls
        self.update_list_devices()

    def scan_again(self, *args):
        Logger.info('SettingsView: scan_again invoked')

        start_scanning()
        Clock.schedule_once(self.update_list_devices, 8)

    def update_list_devices(self, *args):
        Logger.info('SettingsView: updating list of devices')

        self.ids.set_scanned_devices_list_grid.clear_widgets()

        for _urls_settings_list_item in self.settings_scanned_devices:

            self.formated_dev_name_address = '{}/{}'.format(_urls_settings_list_item, self.settings_scanned_devices[_urls_settings_list_item])

            self.ids.set_scanned_devices_list_grid.add_widget(SettingsViewItem(self.formated_dev_name_address))

    def save_settings(self, *args):
        if self.choosen_device:
            Logger.info('save settings set_as_host {}'.format(self.choosen_device))

            self.settings_set_as_host(self.choosen_device)

    def settings_set_as_host(self, host_in):
        breaker = host_in.find('/')
        prepare_url = host_in[:breaker]
        Connector.url = prepare_url

    def return_to_main_view(self, *args):
        self.manager.current = 'main'


class So:
    def __init__(self, **kwargs):
        Logger.info('So: Initialized {}'.format(self))

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(2)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


class Progression(Screen):

    def __init__(self, **kwargs):
        super(Progression, self).__init__(**kwargs)
        Logger.info('Progression: Initialized {}'.format(self))

        self.sch_event = Clock.schedule_interval(self.progression_bar_handler, 0.08) ## slow load
        # self.sch_event = Clock.schedule_interval(self.progression_bar_handler, 1/60) ## fast load

    def progression_bar_handler(self, *args):

        if self.ids.progress_bar_main_image.opacity < 1:

            self.ids.progress_bar_overlay_image.opacity -= 0.005 # fade out overlay
            self.ids.progress_bar_main_image.opacity += 0.01 # fade in main image
            self.ids.progress_bar_overlay_image_t.width -= dp(10)
            self.ids.progress_bar_overlay_image_t.opacity -= 0.02

            if self.ids.progress_bar_main_image.opacity > 0.6:
                self.ids.progress_bar_overlay_image.opacity -= 0.01  # fade out overlay
                self.ids.progress_bar_main_image.opacity += 0.01  # fade in main image

        else:
            Logger.info('Progression: Progress bar scheduler event stopped')

            self.sch_event.cancel()
            Logger.info('Progression: switching to ScanView')

            self.manager.switch_to(ScanView(), transition=FadeTransition(), duration=1)


class ViewControl(ScreenManager):
    Logger.info('Window size {}'.format(Window.size))

    height_x = Window.size[1]
    Logger.info('Window height in dp {}'.format(height_x))

    width_x = Window.size[0]
    Logger.info('Window height in dp {}'.format(width_x))

    def __init__(self, **kwargs):
        super(ViewControl, self).__init__(**kwargs)
        Logger.info('ViewControl: Initialized {}'.format(self))

        self.t1 = threading.Thread(name="Loading screen thread", target=self.init_loading_screen())
        self.t1.start()

        start_scanning()

    def init_loading_screen(self, *args):
        Logger.info('ViewControl: start loading')

        Clock.schedule_once(self.scheduled_start_progression, 3)

    def scheduled_start_progression(self, *args):
        self.add_widget(Progression(name='loading'))


class LoaderOverlay(ModalView):
    def __init__(self, **kwargs):
        super(LoaderOverlay, self).__init__(**kwargs)
        Logger.info('LoaderOverlay: Initialized {}'.format(self))

        self.size = (Window.size[0] / 1.5, Window.size[1] / 1.5)


class ConnectionErrorPopup(Popup):
    def __init__(self, **kwargs):
        super(ConnectionErrorPopup, self).__init__(**kwargs)
        Logger.info('ConnectionErrorPopup: Initialized {}'.format(self))

        self.size = (Window.size[0] / 1.5, Window.size[1] / 1.5)

    def quit_app_cl(self, *args):
        Logger.info('Quit app')

        App.stop(App.get_running_app())

    def retry(self, *args):
        Logger.info('ConnectionErrorPopup: retry to connection')

        self.dismiss()
        App.get_running_app().root.clear_widgets()
        App.get_running_app().root.add_widget(ViewControl())
        Logger.info('ConnectionErrorPopup: refreshing view')


class MediaServiceMclientApp(App):

    def build(self):
        Logger.info('Application : Initialized {}'.format(self))

        self.root = BoxLayout(orientation='vertical')
        self.root.bind(on_keyboard=self.key_input)
        self.loader_overlay = LoaderOverlay()
        self.conn_error_popup = ConnectionErrorPopup()

        return self.root

    def on_start(self):
        self.root.add_widget(ViewControl())

    def quit_app(self, *args):
        self.stop()

    def on_pause(self):
        return True

    def key_input(self, window, key, scancode, codepoint, modifier):
        if key == 27:
            return True  # override the default behaviour
        else:  # the key now does nothing
            return False

if __name__ == '__main__':

    MediaServiceMclientApp().run()
