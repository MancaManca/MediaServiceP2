from kivy import Logger
from kivy.app import App
from kivy.clock import mainthread, Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.properties import ObjectProperty, BooleanProperty, StringProperty, partial
from kivy.storage.jsonstore import JsonStore
from kivy.uix.accordion import Accordion, AccordionItem
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import AsyncImage, Image
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.utils import get_color_from_hex

from Crypto.Hash import SHA256

import requests
import socket
import threading

#######################################____________SCAN___________________######################################


def scan_network_for_single_connection(_subnet):
    Logger.info('Network scanning initializes on thread {}'.format(threading.currentThread().getName()))

    network_address = '192.168.0.{}'.format(_subnet)
    Logger.info('Scanner for {}'.format(network_address))
    # network = '10.85.180.{}'.format(_subnet)
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

#######################################____________SCAN___________________######################################


#######################################____________API_REQUESTS___________________######################################


hashed_dic_shows = {}
hashed_dic_show = {}
hashed_dic_movie = {}
hashed_dic_movies = {}
hashed_dic_search = {}
scanned_online_urls = {}
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
        except:
            App.get_running_app().conn_error_popup.open()
            Logger.warning('no connection')

    def get_search_by_id(self):
        self._url_prepared = self.short_url + self.query['_id']
        try:
            return requests.get(self._url_prepared)
        except:
            App.get_running_app().conn_error_popup.open()
            Logger.warning('no connection')

    def get_pages(self):
        try:
            return requests.get(self.url)
        except:
            App.get_running_app().conn_error_popup.open()
            Logger.warning('no connection')


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

# pippp = Shows().get_pages()
# pippp = Shows(_id = 'tt4209752').get_search_by_id()
# pippp = Shows(genre='animation', order='1', sort='name').get_search()
# pippp = Shows(page='1', order='1', sort='updated').get_search()
# pippp = Movies().get_pages()
# pippp = Movies(keywords='mission impossible', order='1', sort='name').get_search()
# pippp = Movies(_id = 'tt0120755').get_search_by_id()

def hash_item_m(x):
    to_hash = '{}'.format(x)
    hashed_item = SHA256.new(to_hash.encode()).hexdigest()
    return hashed_item


def hash_item(__json_in, method_flag): # requires JSON object
    __json_hashed_out = {}
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

    if Shows().short_url in _api_call_response.url:
        populate_hashed_json_dic(hash_item(_api_call_response.json(), False), hashed_dic_show)
    if Movies().short_url in _api_call_response.url:
        populate_hashed_json_dic(hash_item(_api_call_response.json(), False), hashed_dic_movie)
    if Movies().url in _api_call_response.url:
        populate_hashed_json_dic(hash_item(_api_call_response.json(), True), hashed_dic_movies)
    if Shows().url in _api_call_response.url:
        populate_hashed_json_dic(hash_item(_api_call_response.json(), True), hashed_dic_shows)


def get_api(_api_call):
    try:
        api_request_handler(_api_call)
        api_request_controler(_api_call)
    except:
        Logger.info('caught at get api')
        raise Exception

#######################################____________API_REQUESTS___________________######################################

#######################################____________CONNECTOR___________________#########################################


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

        except:
            Logger.info('no connection to server')

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
            Logger.info('No connection to server')

    def receive(self, *args):
        responded_msg = self.sock.recv(2048)
        # Logger.info(responded_msg.decode())
        if not len(responded_msg.decode()):
            Logger.info('false')

            self.server_state = False
            try:
                self.sock.close()
            except OSError:
                Logger.info('not able to close')

                pass
            self.connects(self.host, self.port)

        else:
            self.server_state = True
            Logger.info('true')

#######################################____________CONNECTOR___________________#########################################


def start_loade(*args):
    App.get_running_app().loader_overlay.open()
    Logger.info('start')


def stop_loade(*args):
    App.get_running_app().loader_overlay.dismiss()
    Logger.info('stop')


def busy_loading_overlay(entry, finish):
    Clock.schedule_once(start_loade,entry)
    Clock.schedule_once(stop_loade, finish)

#######################################____________APP___________________#########################################


class MoviesViewMainSingle(Screen):
    def __init__(self, movie_id, **kwargs):
        super(MoviesViewMainSingle, self).__init__(**kwargs)
        self.movie_id = movie_id
        self.name = 'mvms'
        self.blak = self
        Logger.info('MoviesViewMainSingle: Initialized {}'.format(self))
        self.ids.mvmsingle.add_widget(Label(text=self.name))
        self.ids.mvmsingle.add_widget(Button(text='back', on_press = self.go_back_to_movies))
        self.ids.mvmsingle.add_widget(Button(text='send', on_press = lambda x: self.send_me('single ladies')))

        get_api(Movies(_id = self.movie_id).get_search_by_id())
        for i in hashed_dic_movie:
            for b in hashed_dic_movie[i]:
                vale = '{} {}'.format(b, hashed_dic_movie[i][b])
                self.ids.mvmsingle.add_widget(Label(text=vale))

        self.movies_single_connector = Connector()


    def send_me(self, msg, *args):
        self.movies_single_connector.mysend(msg)


    def go_back_to_movies(self,*args):
        if 'latest view main screen' in self.manager.screen_names:
            Logger.info('back from latest')
            self.manager.current = 'latest view main screen'

        else:
            Logger.info('back from series')
            self.manager.current = 'movies view main screen'
        self.manager.remove_widget(self.blak)

class MoviesViewMain(Screen):
    def __init__(self, **kwargs):
        super(MoviesViewMain, self).__init__(**kwargs)
        Logger.info('MoviesViewMain: Initialized {}'.format(self))
        self.name = 'movies view main screen'

        movies_layout = GridLayout(cols=3, padding=20, spacing=20,
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

            self._items.add_widget(Label(text=hashed_dic_movies[_movie]['title'], size_hint_y=.1, text_size=(((Window.size[0] / 3)-45), None), shorten_from='right', halign='center', shorten=True))
            self._items.add_widget(Button(text='show', size_hint_y=.1, on_press=partial(self.change_to_movies_single, self._items.megs)))

            movies_layout.add_widget(self._items)

    def async_image_error_load(self, instance, *args):
        Logger.info('MoviesViewMain: Async image failed {}'.format(instance))

        instance.source = './images/logo.png'

    def change_to_movies_single(instance, __movie_id, *args):
        Logger.info('MoviesViewMain: change_to_movies_single {}'.format(__movie_id))

        instance.manager.add_widget(MoviesViewMainSingle(__movie_id))
        instance.manager.current = 'mvms'


class ScMaMovies(ScreenManager):
    def __init__(self, **kwargs):
        super(ScMaMovies, self).__init__(**kwargs)
        Logger.info('ScMaMovies: Initialized {}'.format(self))

        if MoviesView.skipper:
            Clock.schedule_once(self.add_scmm, 0)
        else:

            Clock.schedule_once(self.start_loade, -1)
            Clock.schedule_once(self.add_scmm, 0.5)
            Clock.schedule_once(self.stop_loade, 5)

    def start_loade(self, *args):
        App.get_running_app().loader_overlay.open()
        Logger.info('start')

    def stop_loade(self,*args):
        App.get_running_app().loader_overlay.dismiss()
        Logger.info('stop')

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

        self.movies_paginator = GridLayout(rows=1, cols=50, padding=5, spacing=5, size_hint=(None,None))
        self.movies_paginator.bind(minimum_width=self.movies_paginator.setter('width'))

        for i in range(1,50):
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
            if self._filter_order == None:
                self._filter_order = '-1'
            if self._filter_sort == None:
                self._filter_sort = 'last added'

            get_api(Movies(page=paginator_button_instance.text, order=self._filter_order, sort=self._filter_sort, genre=self._filter_genre).get_search())
            self.ids.mov_view_holder.add_widget(ScMaMovies())
        except Exception :
            App.get_running_app().conn_error_popup.open()
            pass


class Item(BoxLayout):
    def __init__(self, sname, **kwargs):
        super(Item, self).__init__(**kwargs)
        Logger.info('Item: Initialized {}'.format(self))
        self.megs = sname
        Logger.info('Item: sname {}'.format(self.megs))

        self.popup = Popup(title='Test popup',
                      content=Label(text=self.megs),
                      size_hint=(None, None), size=(600, 600))

class SeriesViewMainSingleTop(BoxLayout):
    def __init__(self, sh_year, sh_synopsis, sh_runtime, sh_image, **kwargs):
        super(SeriesViewMainSingleTop, self).__init__(**kwargs)
        Logger.info('SeriesViewMainSingleTop: Initialized {}'.format(self))
        self._sh_year = sh_year
        self._sh_synopsis = sh_synopsis
        self._sh_runtime = sh_runtime
        self._sh_image = sh_image

        self.ids.series_view_main_single_top_im_holder.add_widget(AsyncImage(source=self._sh_image))
        self.ids.series_view_main_single_top_other.add_widget(Label(text=str(self._sh_year),unicode_errors='ignore',size_hint_y=.1))
        self.ids.series_view_main_single_top_other.add_widget(Label(text=str(self._sh_runtime), size_hint_y=.1))
        self.ids.series_view_main_single_top_other.add_widget(TextInput(text=self._sh_synopsis,unicode_errors='ignore',readonly=True,multi_line=True,size_hint_y=.8))



class SeriesViewMainSingle(Screen):
    def __init__(self, series_id, **kwargs):
        super(SeriesViewMainSingle, self).__init__(**kwargs)
        self.series_single_connector = Connector()

        self.series_id = series_id
        self.name = 'svms'
        self.blak = self

        Logger.info('SeriesViewMainSingle: Initialized {}'.format(self))


        # self.ids.series_view_main_single_nav.add_widget(Button(text='send',on_press = lambda x: self.send_me('single ladies')))


        get_api(Shows(_id=self.series_id).get_search_by_id())

        for i in hashed_dic_show:
            for b in hashed_dic_show[i]:

                if b =='episodes':

                    self.b = Accordion(orientation='vertical', height=180 * int(len(hashed_dic_show[i]['episodes'])), size_hint_y=None)
                    # self.b.content_size = [40, 40]
                    self.b.id = 'testAccordian'

                    self.g_scroll_list = ScrollView(size_hint=(None, None),
                                                    size=(ViewControl.width_x - 40, ViewControl.height_x * 0.4),
                                                    pos_hint={'center_x': 0.5, 'center_y': 0.5})

                    self.ids.series_view_main_single_container_se.add_widget(self.g_scroll_list)
                    self.g_scroll_list.add_widget(self.b)

                    Logger.info('Show level >>>>>')
                    self.ids.series_view_main_single_container.add_widget(SeriesViewMainSingleTop(hashed_dic_show[i]['year'],hashed_dic_show[i]['synopsis'],hashed_dic_show[i]['runtime'],hashed_dic_show[i]['images']['poster']))

                    Logger.info(hashed_dic_show[i]['title'])
                    self.ids.series_view_main_single_nav_title.add_widget(Label(text=hashed_dic_show[i]['title'].encode('utf-8',errors='ignore'),unicode_errors='ignore'))

                    Logger.info(hashed_dic_show[i]['year'])
                    Logger.info(hashed_dic_show[i]['synopsis'])
                    Logger.info(hashed_dic_show[i]['runtime'])
                    Logger.info(hashed_dic_show[i]['images']['poster'])
                    Logger.info(len(hashed_dic_show[i]['episodes']))
                    self._ep_num = len(hashed_dic_show[i]['episodes'])



                    for z in hashed_dic_show[i][b]:
                        acc_item = AccordionItem(collapse=True, orientation='vertical')

                        acc_item.container.orientation = 'vertical'
                        Logger.info('Episode level >>>>>')
                        # Logger.info(z)
                        Logger.info(z['title'])
                        Logger.info(z['overview'])
                        Logger.info(z['episode'])
                        Logger.info(z['season'])
                        Logger.info(z['torrents'])

                        if z['title']:
                            ti = z['title'].encode('utf-8')
                        else:
                            ti = ''

                        sea = str(z['season'])
                        sea = sea.encode('utf-8')
                        epi  = str(z['episode'])
                        epi = epi.encode('utf-8')
                        if z['overview']:
                            over = z['overview'].encode('utf-8')
                        else:
                            over = ''

                        tor = str(z['torrents'])
                        tor = tor.encode('utf-8')
                        acc_item.title = '{} {} {}'.format(ti,sea,epi)

                        acc_item.container.add_widget(TextInput(text=str(over), unicode_errors='ignore',multi_line=True))
                        acc_item.container.add_widget(TextInput(text=str(tor), unicode_errors='ignore',multi_line=True))

                        # self.z.add_widget(Label(text=' acc item {}'.format(i)))
                        self.b.add_widget(acc_item)

                        # Logger.info(hashed_dic_show[i][b][z])

                # vale = '{} {}'.format(b, hashed_dic_show[i][b])
                # self.ids.svmsingle.add_widget(Label(text=vale, max_lines=2))









    def send_me(self, msg, *args):
        self.series_single_connector.mysend(msg)



    def pr(self, *args):
        # Logger.info(self.parent)
        # Logger.info(self.manager.screens)
        # Logger.info(' MainView {}'.format(self.parent))
        # Logger.info(self.manager.screen_names)
        pass

    def go_back_to_series(self,*args):

        if 'latest view main screen' in self.manager.screen_names:
            Logger.info('back from latest')
            self.manager.current = 'latest view main screen'

        else:
            Logger.info('back from series')
            self.manager.current = 'series view main screen'
        self.manager.remove_widget(self.blak)


class SeriesViewMain(Screen):
    def __init__(self, **kwargs):
        super(SeriesViewMain, self).__init__(**kwargs)
        Logger.info('SeriesViewMain: Initialized {}'.format(self))
        self.name = 'series view main screen'

        series_layout = GridLayout(cols=3, padding=20, spacing=20,
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
            except:
                Logger.info('No image setting default')

                self._items.add_widget(Image(source='/images/logo.png'))
                pass

            self._items.add_widget(Label(text=hashed_dic_shows[_show]['title'], size_hint_y=.1, text_size=(((Window.size[0] / 3)-45), None), shorten_from='right', halign='center', shorten=True))
            self._items.add_widget(Button(text='show', size_hint_y=.1, on_press=partial(self.change_to_series_single, self._items.megs)))

            series_layout.add_widget(self._items)

    def async_image_error_load(self, instance, *args):
        Logger.info('SeriesViewMain: Async image failed {}'.format(instance))

        instance.source = './images/logo.png'

    def change_to_series_single(instance, __show_id, *args):
        Logger.info('SeriesViewMain: change_to_series_single {}'.format(__show_id))


        Clock.schedule_once(instance.start_loade, -1)
        Clock.schedule_once(partial(instance.add_scms,__show_id), 0.5)
        Clock.schedule_once(instance.stop_loade, 8)

    def start_loade(self, *args):
        App.get_running_app().loader_overlay.open()
        Logger.info('start')

    def stop_loade(self, *args):
        App.get_running_app().loader_overlay.dismiss()
        Logger.info('stop')

    def add_scms(self, __s_id, *args):
        self.manager.add_widget(SeriesViewMainSingle(__s_id))
        self.manager.current = 'svms'


class ScMaSeries(ScreenManager):
    def __init__(self, **kwargs):
        super(ScMaSeries, self).__init__(**kwargs)
        Logger.info('ScMaSeries: Initialized {}'.format(self))

        if SeriesView.skipper:
            Clock.schedule_once(self.add_scms, 0)
        else:

            Clock.schedule_once(self.start_loade, -1)
            Clock.schedule_once(self.add_scms, 0.5)
            Clock.schedule_once(self.stop_loade, 5)

    def start_loade(self, *args):
        App.get_running_app().loader_overlay.open()
        Logger.info('start')

    def stop_loade(self, *args):
        App.get_running_app().loader_overlay.dismiss()
        Logger.info('stop')

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
            if self._filter_order == None:
                self._filter_order = '-1'
            if self._filter_sort == None:
                self._filter_sort = 'updated'
            paginator_button_instance.background_color = get_color_from_hex('#ffa500')
            get_api(Shows(page=paginator_button_instance.text, order=self._filter_order, sort=self._filter_sort, genre=self._filter_genre).get_search())
            self.ids.ser_view_holder.add_widget(ScMaSeries())
        except Exception:
            App.get_running_app().conn_error_popup.open()
            pass


class SearchView(Screen):
    def __init__(self, **kwargs):
        super(SearchView, self).__init__(**kwargs)
        Logger.info('SearchView: Initialized {}'.format(self))
        # Logger.info(self.ids)

    def set_to_cur(self, scn, *args):
        self.manager.current = scn

        Clock.schedule_once(self.pr, 9)

    def pr(self, *args):
        # Logger.info(self.parent)
        # Logger.info(self.manager.screens)
        # Logger.info(' MainView {}'.format(self.parent))
        # Logger.info(self.manager.screen_names)
        pass

    pass


class LatestViewMain(Screen):
    def __init__(self, **kwargs):
        super(LatestViewMain, self).__init__(**kwargs)

        Logger.info('LatestViewMain: Initialized {}'.format(self))

        self.name = 'latest view main screen'
#################________________SHOWS LATEST______________##########################
        latest_series_layout = GridLayout(cols=3, padding=20, spacing=20,
                                   size_hint=(None, None), width=ViewControl.width_x - 30)
        latest_series_layout.bind(minimum_height=latest_series_layout.setter('height'))

        latest_series_scroll_list = ScrollView(size_hint=(None, None),
                                        size=(ViewControl.width_x - 20, ViewControl.height_x * 0.45),
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
                except:
                    Logger.info('No image setting default')

                    self._items_latest_s.add_widget(Image(source='/images/logo.png'))
                    pass

                self._items_latest_s.add_widget(Label(text=hashed_dic_shows[_show]['title'], size_hint_y=.1, text_size=(((Window.size[0] / 3)-45), None), shorten_from='right', halign='center', shorten=True))
                self._items_latest_s.add_widget(Button(text='show', size_hint_y=.1, on_press=partial(self.change_to_series_single, self._items_latest_s.megs)))

                latest_series_layout.add_widget(self._items_latest_s)
                latest_show_counter += 1

#################________________MOVIES LATEST______________##########################

        latest_movies_layout = GridLayout(cols=3, padding=20, spacing=20,
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
                except:
                    Logger.info('No image setting default')

                    self._items_latest_m.add_widget(Image(source='images/logo.png'))
                    pass

                self._items_latest_m.add_widget(Label(text=hashed_dic_movies[_movie]['title'], size_hint_y=.1,
                                             text_size=(((Window.size[0] / 3) - 45), None), shorten_from='right',
                                             halign='center', shorten=True))
                self._items_latest_m.add_widget(
                    Button(text='show', size_hint_y=.1, on_press=partial(self.change_to_movies_single, self._items_latest_m.megs)))

                latest_movies_layout.add_widget(self._items_latest_m)
                latest_movie_counter += 1


    def async_image_error_load(self, instance, *args):
        Logger.info('LatestViewMain: Async image failed {}'.format(instance))

        instance.source = './images/logo.png'

    def change_to_series_single(instance, __show_id, *args):
        Logger.info('LatestViewMain: change_to_series_single {}'.format(__show_id))

        instance.manager.add_widget(SeriesViewMainSingle(__show_id))
        instance.manager.current = 'svms'

    def change_to_movies_single(instance, __movie_id, *args):
        Logger.info('MoviesViewMain: change_to_movies_single {}'.format(__movie_id))

        instance.manager.add_widget(MoviesViewMainSingle(__movie_id))
        instance.manager.current = 'mvms'

class ScMaLatest(ScreenManager):

    def __init__(self, **kwargs):
        super(ScMaLatest, self).__init__(**kwargs)
        Logger.info('ScMaLatest: Initialized {}'.format(self))

        if LatestView.skipper:
            Clock.schedule_once(self.add_scms, 0)
        else:

            Clock.schedule_once(self.start_loade, -1)
            Clock.schedule_once(self.add_scms, 0.5)
            Clock.schedule_once(self.stop_loade, 5)

    def start_loade(self, *args):
        App.get_running_app().loader_overlay.open()
        Logger.info('start')

    def stop_loade(self, *args):
        App.get_running_app().loader_overlay.dismiss()
        Logger.info('stop')

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
        # Logger.info(self.ids)
        self.ids.lat_view_holder.add_widget(ScMaLatest())


    def refresh_on_enter(self, *args):
        if not LatestView.skipper:
            self.ids.lat_view_holder.remove_widget(self.ids.lat_view_holder.children[0])

            try:
                get_api(Shows(order='-1', sort='updated',
                              genre=self._filter_genre).get_search())
                get_api(Movies(order='-1', sort='last added',
                              genre=self._filter_genre).get_search())
                self.ids.lat_view_holder.add_widget(ScMaLatest())
            except Exception:
                App.get_running_app().conn_error_popup.open()
                pass


class MainViewScManager(ScreenManager):
    def __init__(self, **kwargs):
        super(MainViewScManager, self).__init__(**kwargs)
        Logger.info('MainViewScManager: Initialized {}'.format(self))
        self.add_widget(SearchView())
        self.add_widget(LatestView())
        self.add_widget(MoviesView())
        self.add_widget(SeriesView())


class FilterModalView(ModalView):
    def __init__(self, **kwargs):
        super(FilterModalView, self).__init__(**kwargs)
        Logger.info('FilterModalView: Initialized {}'.format(self))
        self.size = (Window.size[0] / 1.5, Window.size[1] / 1.5)
        self.ids.filter_genre.dropdown_cls.max_height = dp(250)

    def close_filter(self, filter_type, filter_genre, filter_order, filter_sort):
        self.filter_type = filter_type
        # if filter_type == 'Shows' or filter_type == 'Movies'
        self.filter_genre = filter_genre
        self.filter_order = filter_order
        self.filter_sort = filter_sort

        if filter_genre == 'Genre':
            self.filter_genre = None
        if filter_order == 'Order':
            self.filter_order = None
        if filter_sort == 'Sort':
            self.filter_sort = None

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


    def hide_other_accordions(instances,selfi):
        for spinner_child in instances.ids.filter_view_container.children[0].children:
            spinner_child.opacity = 0.2
        selfi.opacity = 1



class MainView(Screen):
    connection_status_indicator = BooleanProperty(None)

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
            Logger.info('MainView: update connection indicator to {}'.format(self.connector.server_state))

        else:
            Logger.info('MainView: update connection indicator to {}'.format(self.connector.server_state))

            self.update_status_in(self.connector.server_state)

    def open_filter_view(self, *args):
        Logger.info('MainView: open_filter_view invoked')

        self.view.open()

    def set_as_current_screen(self, button_instance, scn, other_but_f, other_but_s, *args):
        Logger.info('MainView: setting active screen {}'.format(scn))

        button_instance.background_normal = "./images/n_b.png"
        other_but_f.background_normal = "./images/n_n.png"
        other_but_s.background_normal = "./images/n_n.png"
        self.main_scm.current = scn

    def set_as_current_screen_search(self, scn, ot_1, ot_2, ot_3, o1,o2):
        Logger.info('MainView: setting active screen for search {}'.format(scn))

        ot_1.background_normal = "./images/n_n.png"
        ot_2.background_normal = "./images/n_n.png"
        ot_3.background_normal = "./images/n_n.png"

        self.main_scm.current = scn

    def focu_defocu(instance, tex , fla,*args):
        if fla:
            tex.opacity = 1
        else:
            tex.opacity = .2

    def navigate_to_settings(self, *args):
        Logger.info('MainView: navigate_to_settings invoked')

        if 'settings' not  in self.manager.screen_names:
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

        self._urls_list = scanned_online_urls

        for _urls_list_item in self._urls_list:
            self.formated_dev_name_address = '{}/{}'.format(_urls_list_item, self._urls_list[_urls_list_item])
            self.ids.scanned_devices_list_grid.add_widget(ScanViewItem(self.formated_dev_name_address))

#################################_________________API_IMPL__________________________####################################

        self.start_service()

    def start_service(self, *args):
        Logger.info('ScanView: start service invoked')

        """get inital latest movies and series, populate shows dictionary populate movies dicionary"""
        try:
            get_api(Shows(order='-1', sort='updated').get_search())
            get_api(Movies(order='-1', sort='last added').get_search())
            Logger.info('ScanView: start service sucess')

        except:
            Logger.info('ScanView: start service fail')

            App.get_running_app().conn_error_popup.open()
            pass


#################################_________________API_IMPL__________________________####################################

    def set_as_host(self, host_in):
        Logger.info('init scan set_as_host')

        breaker = host_in.find('/')
        prepare_url = host_in[:breaker]
        Connector.url = prepare_url

    def save_and_go_to_main(self, *args):
        if self.choosen_device:
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

        self.ids.settings_view_container_list_container.clear_widgets()

        for _urls_settings_list_item in self.settings_scanned_devices:

            self.formated_dev_name_address = '{}/{}'.format(_urls_settings_list_item, self.settings_scanned_devices[_urls_settings_list_item])

            self.ids.settings_view_container_list_container.add_widget(SettingsViewItem(self.formated_dev_name_address))

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
        self.loader_overlay = LoaderOverlay()
        self.conn_error_popup = ConnectionErrorPopup()

        return self.root

    def on_start(self):
        self.root.add_widget(ViewControl())

    def quit_app(self, *args):
        self.stop()

    def on_pause(self):
        return True


if __name__ == '__main__':

    MediaServiceMclientApp().run()

