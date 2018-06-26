from kivy import Logger
from kivy.app import App
from kivy.clock import mainthread, Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.properties import ObjectProperty, BooleanProperty, StringProperty
from kivy.storage.jsonstore import JsonStore
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
            # ScanView.urls_list[network_address] = str(responded_msgs.decode())
            scanned_online_urls[network_address] = str(responded_msgs.decode())

            Logger.info('Server on address {} responded with message {}'.format(network_address,
                                                                                str(responded_msgs.decode())))
            s.sock.close()

        else:
            Logger.info('{} responded {}'.format(network_address, _socket))

    finally:
        s.sock.close()
        Logger.info(
            'Current :{} Exiting for {} and closing {}'.format(threading.currentThread().getName(), _subnet, s))


def start_scanning(*args):
    for _subnet_in in range(9, 13):
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
# current = None

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

        # Logger.info(self._url_prepared)
        return requests.get(self._url_prepared)

    def get_search_by_id(self):

        self._url_prepared = self.short_url + self.query['_id']
        # priLogger.infont(self._url_prepared)
        return requests.get(self._url_prepared)

    def get_pages(self):
        return requests.get(self.url)


class Movies(api):
    def __init__(self, page=None, sort=None, order=None, keywords=None, _id=None, genre=None, **kwargs):

        self.url = self._url('/movies')
        self.short_url = self._url('/movie/')
        self.query = {}

        if page:
            self.query['page'] = page
        if sort:
            self.query['sort'] = str(sort).replace(' ', '%20')
        if order:
            self.query['order'] = order
        if _id:
            self.query['_id'] = _id
        if genre:
            self.query['genre'] = genre
        if keywords:
            self.query['keywords'] = str(keywords).replace(' ', '%20')

class Shows(api):
    def __init__(self, page=None, sort=None, order=None, keywords=None, _id=None, genre=None, **kwargs):

        self.url = self._url('/shows')
        self.short_url = self._url('/show/')
        self.query = {}

        if page:
            self.query['page'] = page
        if sort:
            self.query['sort'] = str(sort).replace(' ', '%20')
        if order:
            self.query['order'] = order
        if _id:
            self.query['_id'] = _id
        if genre:
            self.query['genre'] = genre
        if keywords:
            self.query['keywords'] = str(keywords).replace(' ', '%20')

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
    return  hashed_item

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
    Logger.info(_api_call.url)

    try:
        api_request_handler(_api_call)
        api_request_controler(_api_call)
    except Exception as e:
        Logger.info(e)
#######################################____________API_REQUESTS___________________######################################




#######################################____________CONNECTOR___________________#########################################
class Connector:
    url = ''
    def __init__(self, **kwargs):
        Logger.info('Connector: Initialized {}'.format(self))


        # self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.url:
            self.host = self.url
            # Logger.info(self.host)
        else:
            # self.host = '192.168.0.10'
            self.host = None
        self.port = 8000
        self.server_state = True
        # MainView.mika(True)

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
            # MainView.connection_status_indicator = False
            # MainView.mika(False)

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
            # MainView.connection_status_indicator = False
            # MainView.mika(False)
            try:
                self.sock.close()
            except OSError:
                Logger.info('not able to close')
                pass
            self.connects(self.host, self.port)

        else:
            self.server_state = True
            # MainView.connection_status_indicator = True
            # MainView.mika(True)
            Logger.info('true')

#######################################____________CONNECTOR___________________#########################################

#######################################____________APP___________________#########################################


class MoviesViewMainSingle(Screen):
    def __init__(self, movie_id, **kwargs):
        super(MoviesViewMainSingle, self).__init__(**kwargs)
        self.movie_id = movie_id
        self.name = 'mvms'
        self.blak = self
        Logger.info('MoviesViewMainSingle: Initialized {}'.format(self))
        self.ids.mvmsingle.add_widget(Label(text=self.name))
        self.ids.mvmsingle.add_widget(Button(text='back',on_press = self.go_back_to_movies))
        self.ids.mvmsingle.add_widget(Button(text='send',on_press = lambda x: self.send_me('single ladies')))

        get_api(Movies(_id = self.movie_id).get_search_by_id())
        for i in hashed_dic_movie:
            for b in hashed_dic_movie[i]:
                self.ids.mvmsingle.add_widget(Label(text=b))

        self.movies_single_connector = Connector()




    def send_me(self, msg, *args):
        self.movies_single_connector.mysend(msg)



    def pr(self, *args):
        # Logger.info(self.parent)
        # Logger.info(self.manager.screens)
        # Logger.info(' MainView {}'.format(self.parent))
        # Logger.info(self.manager.screen_names)
        pass

    def go_back_to_movies(self,*args):
        self.manager.current = 'movies view main screen'
        self.manager.remove_widget(self.blak)

class MoviesViewMain(Screen):
    def __init__(self, **kwargs):
        super(MoviesViewMain, self).__init__(**kwargs)
        Logger.info('MoviesViewMain: Initialized {}'.format(self))
        self.name = 'movies view main screen'

        movies_layout = GridLayout(cols=3, padding=20, spacing=20,
                            size_hint=(None, None), width=ViewControl.width_x - 30)

        # when we add children to the grid layout, its size doesn't change at
        # all. we need to ensure that the height will be the minimum required
        # to contain all the childs. (otherwise, we'll child outside the
        # bounding box of the childs)
        movies_layout.bind(minimum_height=movies_layout.setter('height'))

        movies_scroll_list = ScrollView(size_hint=(None, None), size=(ViewControl.width_x - 20, ViewControl.height_x*0.75),
                          pos_hint={'center_x': 0.5, 'center_y': 1}, do_scroll_x=False)
        movies_scroll_list.add_widget(movies_layout)
        # Logger.info(self.ids)
        self.ids.movies_view_main_container.add_widget(movies_scroll_list)

        for kk in hashed_dic_movies:
            #     Logger.info('{}----{}'.format(kk, hashed_dic_grouop[kk]))
            _items = Item(hashed_dic_movies[kk]['_id'])
            _items.size = ((Window.size[0] / 3) - 30, (Window.size[1] / 2) - 200)
            try:
                _items.add_widget(AsyncImage(source=hashed_dic_movies[kk]['images']['poster'], nocache=True))
            except Exception as e:
                pass
                Logger.info('No image setting default cause of {}'.format(e))
                _items.add_widget(Image(source='images/logo.png'))
            _items.add_widget(Label(text=hashed_dic_movies[kk]['title'], size_hint_y=.1,text_size=(((Window.size[0] / 3)-45), None),shorten_from='right',halign='center',shorten=True))
            _items.add_widget(Button(text = 'show',on_press = lambda x: self.change_to_movies_single(hashed_dic_movies[kk]['_id']),size_hint_y=.1))

            movies_layout.add_widget(_items)


    def change_to_movies_single(self, x,*args):
        # Logger.info(self.manager)

        self.manager.add_widget(MoviesViewMainSingle(x))
        self.manager.current = 'mvms'

class ScMaMovies(ScreenManager):
    def __init__(self, **kwargs):
        super(ScMaMovies, self).__init__(**kwargs)
        Logger.info('ScMaMovies: Initialized {}'.format(self))
        self.add_widget(MoviesViewMain())


class MoviesView(Screen):
    def __init__(self, **kwargs):
        super(MoviesView, self).__init__(**kwargs)
        Logger.info('MoviesView: Initialized {}'.format(self))
        Clock.schedule_once(self.pr, 9)


        self.movies_paginator = GridLayout(rows=1,cols=50,padding=5, spacing=5,size_hint=(None,None))
        self.movies_paginator.bind(minimum_width=self.movies_paginator.setter('width'))
        for i in range(1,50):
            self.btn = Button(text=str(i),on_press=lambda instance: self.set_p(instance), size_hint=(None, None), size=(100,80))
            self.movies_paginator.add_widget(self.btn)
        self.scroll = ScrollView(size_hint=(1, 1), do_scroll_x=True, do_scroll_y=False)

        self.scroll.add_widget(self.movies_paginator)
        self.ids.movies_pag_holder.add_widget(self.scroll)

        self.ids.mov_view_holder.add_widget(ScMaMovies())

    def set_to_cur(self, scn, *args):
        self.manager.current = scn

    def pr(self, *args):
        # Logger.info(self.parent)
        # Logger.info(self.manager.screens)
        # Logger.info(' MainView {}'.format(self.parent))
        # Logger.info(self.manager.screen_names)
        pass

    def set_p(instance,num,*args):
        # Logger.info(self)
        # Logger.info(num)
        # Logger.info('num {}'.format(num.text))
        # Logger.info('ist {}'.format(instance))
        # Logger.info(instance.ids.mov_view_holder.children)
        instance.ids.mov_view_holder.remove_widget(instance.ids.mov_view_holder.children[0])
        get_api(Movies(page=num.text,order='-1', sort='name').get_search())

        instance.ids.mov_view_holder.add_widget(ScMaMovies())

    pass


class Item(BoxLayout):
    def __init__(self,sname, **kwargs):
        super(Item, self).__init__(**kwargs)
        Logger.info('Item: Initialized {}'.format(self))
        self.megs = sname
        self.popup = Popup(title='Test popup',
                      content=Label(text=self.megs),
                      size_hint=(None, None), size=(600, 600))
    def oppop(self, *args):

        self.popup.open()

    def change_to_movies_single(self,*args):
        # Logger.info(ScMaMovies)

        ScMaMovies.add_widget(MoviesViewMainSingle(self.megs))
        ScMaMovies.current = 'mvms'

class SeriesViewMainSingle(Screen):
    def __init__(self, series_id, **kwargs):
        super(SeriesViewMainSingle, self).__init__(**kwargs)
        self.series_id = series_id
        self.name = 'svms'
        self.blak = self
        Logger.info('SeriesViewMainSingle: Initialized {}'.format(self))
        self.ids.svmsingle.add_widget(Label(text=self.name))
        self.ids.svmsingle.add_widget(Button(text='back',on_press = self.go_back_to_series))
        self.ids.svmsingle.add_widget(Button(text='send',on_press = lambda x: self.send_me('single ladies')))

        get_api(Shows(_id = self.series_id).get_search_by_id())
        for i in hashed_dic_show:
            for b in hashed_dic_show[i]:
                self.ids.svmsingle.add_widget(Label(text=b))

        self.series_single_connector = Connector()




    def send_me(self, msg, *args):
        self.series_single_connector.mysend(msg)



    def pr(self, *args):
        # Logger.info(self.parent)
        # Logger.info(self.manager.screens)
        # Logger.info(' MainView {}'.format(self.parent))
        # Logger.info(self.manager.screen_names)
        pass

    def go_back_to_series(self,*args):
        self.manager.current = 'series view main screen'
        self.manager.remove_widget(self.blak)

class SeriesViewMain(Screen):
    def __init__(self, **kwargs):
        super(SeriesViewMain, self).__init__(**kwargs)
        Logger.info('SeriesViewMain: Initialized {}'.format(self))
        self.name = 'series view main screen'

        series_layout = GridLayout(cols=3, padding=20, spacing=20,
                                   size_hint=(None, None), width=ViewControl.width_x - 30)

        # when we add children to the grid layout, its size doesn't change at
        # all. we need to ensure that the height will be the minimum required
        # to contain all the childs. (otherwise, we'll child outside the
        # bounding box of the childs)
        series_layout.bind(minimum_height=series_layout.setter('height'))

        series_scroll_list = ScrollView(size_hint=(None, None),
                                        size=(ViewControl.width_x - 20, ViewControl.height_x * 0.75),
                                        pos_hint={'center_x': 0.5, 'center_y': 1}, do_scroll_x=False)
        series_scroll_list.add_widget(series_layout)
        # Logger.info(self.ids)
        self.ids.series_view_main_container.add_widget(series_scroll_list)

        for ss in hashed_dic_shows:
            #     Logger.info('{}----{}'.format(kk, hashed_dic_grouop[kk]))
            _items = Item(hashed_dic_shows[ss]['_id'])
            _items.size = ((Window.size[0] / 3) - 30, (Window.size[1] / 2) - 200)
            try:
                _items.add_widget(AsyncImage(source=hashed_dic_shows[ss]['images']['poster'], nocache=True))
            except Exception as e:
                pass
                Logger.info('No image setting default cause of {}'.format(e))
                _items.add_widget(Image(source='images/logo.png'))
            _items.add_widget(Label(text=hashed_dic_shows[ss]['title'], size_hint_y=.1,text_size=(((Window.size[0] / 3)-45), None),shorten_from='right',halign='center',shorten=True))
            _items.add_widget(Button(text = 'show',on_press = lambda x: self.change_to_series_single(hashed_dic_shows[ss]['_id']),size_hint_y=.1))

            series_layout.add_widget(_items)

    def change_to_series_single(self, x,*args):
        # Logger.info(self.manager)

        self.manager.add_widget(SeriesViewMainSingle(x))
        self.manager.current = 'svms'

class ScMaSeries(ScreenManager):
    def __init__(self, **kwargs):
        super(ScMaSeries, self).__init__(**kwargs)
        Logger.info('ScMaSeries: Initialized {}'.format(self))
        self.add_widget(SeriesViewMain())

class SeriesView(Screen):
    def __init__(self, **kwargs):
        super(SeriesView, self).__init__(**kwargs)
        Logger.info('SeriesView: Initialized {}'.format(self))
        Logger.info('This is window size {}'.format(Window.size))
        Logger.info('This is container size {}'.format(self.size))
        Clock.schedule_once(self.pr, 9)

        self.series_paginator = GridLayout(rows=1, cols=50, padding=5, spacing=5, size_hint=(None, None))
        self.series_paginator.bind(minimum_width=self.series_paginator.setter('width'))
        for i in range(1, 50):
            self.btn = Button(text=str(i), on_press=lambda instance: self.set_p(instance), size_hint=(None, None),
                              size=(100, 80))
            self.series_paginator.add_widget(self.btn)
        self.scroll = ScrollView(size_hint=(1, 1), do_scroll_x=True, do_scroll_y=False)

        self.scroll.add_widget(self.series_paginator)
        self.ids.series_pag_holder.add_widget(self.scroll)

        self.ids.ser_view_holder.add_widget(ScMaSeries())


    def set_to_cur(self, scn, *args):
        self.manager.current = scn

    def pr(self, *args):
        # Logger.info(self.parent)
        # Logger.info(self.manager.screens)
        # Logger.info(' MainView {}'.format(self.parent))
        # Logger.info(self.manager.screen_names)
        pass
    def set_p(instance,num,*args):
        # Logger.info(self)
        # Logger.info(num)
        # Logger.info('num {}'.format(num.text))
        # Logger.info('ist {}'.format(instance))
        # Logger.info(instance.ids.mov_view_holder.children)
        instance.ids.ser_view_holder.remove_widget(instance.ids.ser_view_holder.children[0])
        get_api(Shows(page=num.text, order='-1', sort='name').get_search())

        instance.ids.ser_view_holder.add_widget(ScMaSeries())

    pass
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

class LatestView(Screen):
    def __init__(self, **kwargs):
        super(LatestView, self).__init__(**kwargs)
        Logger.info('LatestView: Initialized {}'.format(self))
        # Logger.info(self.ids)

        Clock.schedule_once(self.pr, 9)


        self.connn = Connector()

    def set_as_current_screen(self, scn, *args):
        self.manager.current = scn

    def cc(self, msg, *args):
        self.connn.mysend(msg)

    def reconnect(self, *args):
        self.connn.connects(self.connn.host,self.connn.port)

    def pr(self, *args):
        # Logger.info(self.parent)
        # Logger.info(self.manager.screens)
        # Logger.info(' MainView {}'.format(self.parent))
        # Logger.info(self.manager.screen_names)
        pass
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




class MainView(Screen):
    connection_status_indicator = BooleanProperty(None)

    def __init__(self, **kwargs):
        super(MainView, self).__init__(**kwargs)
        Logger.info('MainView: Initialized {}'.format(self))
        # Clock.schedule_once(self.pr, 9)


        self.scm = MainViewScManager()
        self.ids.screen_m_container.add_widget(self.scm)


        # Logger.info(self.ids)
        self.view = FilterModalView()
        # self.view.add_widget(Label(text='Hello world'))


    def connect_on_enter(self, *args):
        self.connector = Connector()
        Logger.info(self.connector.server_state)
        if self.connector.server_state:
            self.update_status_in(self.connector.server_state)
        else:
            self.update_status_in(self.connector.server_state)

    def open_modal_view(self, *args):
        self.view.open()

    def set_as_current_screen(self, scn, *args):

        self.scm.current = scn

    def navigate_to_settings(self, *args):
        # Logger.info(self.parent)
        # Logger.info(self.manager.screens)
        # Logger.info(' MainView {}'.format(self.parent))
        # Logger.info(self.manager.screen_names)
        if 'settings' not  in self.manager.screen_names:

            self.manager.switch_to(SettingsView(), transition=FadeTransition())
        else:
            self.manager.current = 'settings'

    def update_status_in(self, status_flagger_flag, *args):
        Logger.info('Updating connection status')

        if status_flagger_flag:
            self.ids.connection_status_ind_l.source = 'images/gr.png'
        else:
            self.ids.connection_status_ind_l.source = 'images/re.png'
    pass

class ScanViewItem(BoxLayout):
    def __init__(self, device_name_for_label, **kwargs):
        super(ScanViewItem, self).__init__(**kwargs)
        Logger.info('ScanViewItem: Initialized {}'.format(self))

        self.dev_name_for_l = device_name_for_label
        self.ids.scan_view_i_name.text = self.dev_name_for_l

    def return_on_active_name(self, scan_item_checkobox_flag, scan_item_checkobox_value,  *args):
        if scan_item_checkobox_flag:

            ScanView.choosen_device = scan_item_checkobox_value

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
        # pippp = Shows(order='1', sort='name').get_search()
        """get inital latest movies and series, populate shows dictionary populate movies dicionary"""
        get_api(Shows(order='-1', sort='name').get_search())
        get_api(Movies(order='-1', sort='name').get_search())
        """"""


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


class SettingsViewItem(BoxLayout):
    def __init__(self, device_name_for_label, **kwargs):
        super(SettingsViewItem, self).__init__(**kwargs)
        Logger.info('SettingsViewItem: Initialized {}'.format(self))

        self.dev_name_for_l = device_name_for_label
        self.ids.settings_view_i_name.text = self.dev_name_for_l

    def return_on_active_name(self, settings_item_checkobox_flag, settings_item_checkobox_value,  *args):
        if settings_item_checkobox_flag:

            SettingsView.choosen_device = settings_item_checkobox_value

        else:
            SettingsView.choosen_device = ''

class SettingsView(Screen):
    choosen_device = StringProperty()

    def __init__(self, **kwargs):
        super(SettingsView, self).__init__(**kwargs)
        Logger.info('SettingsView: Initialized {}'.format(self))

        self.settings_scanned_devices = scanned_online_urls
        # Clock.schedule_once(self.return_to_main_view, 9)
        self.update_list_devices()

    def scan_again(self, *args):
        start_scanning()
        Clock.schedule_once(self.update_list_devices, 8)

    def update_list_devices(self, *args):
        self.ids.settings_view_container_list_container.clear_widgets()

        for _urls_settings_list_item in self.settings_scanned_devices:

            self.formated_dev_name_address = '{}/{}'.format(_urls_settings_list_item, self.settings_scanned_devices[_urls_settings_list_item])

            self.ids.settings_view_container_list_container.add_widget(SettingsViewItem(self.formated_dev_name_address))

    def save_settings(self, *args):
        Logger.info('save settings set_as_host')

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

        # self.sch_event = Clock.schedule_interval(self.progression_bar_handler, 0.08)
        self.sch_event = Clock.schedule_interval(self.progression_bar_handler, 1/60)


    def progression_bar_handler(self, *args):

        if self.ids.progress_bar_main_image.opacity < 1:

            self.ids.progress_bar_overlay_image.opacity -= 0.01 # fade out overlay
            self.ids.progress_bar_main_image.opacity += 0.01 # fade in main image
        else:
            Logger.info('Progression: Progress bar scheduler event stopped')

            self.sch_event.cancel()
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
        self.add_widget(Progression(name='loading'))


class MediaServiceMclientApp(App):

    def build(self):
        Logger.info('Application : Initialized {}'.format(self))

        self.root = BoxLayout(orientation='vertical')

        return self.root

    def on_start(self):
        self.root.add_widget(ViewControl())

    def quit_app(self, *args):
        self.stop()

    def on_pause(self):
        return True


if __name__ == '__main__':

    MediaServiceMclientApp().run()

