from kivy import Logger
from kivy.app import App
from kivy.clock import mainthread, Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.properties import ObjectProperty
from kivy.storage.jsonstore import JsonStore
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import AsyncImage, Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.scrollview import ScrollView

from kivy.utils import get_color_from_hex
from Crypto.Hash import SHA256

import socket
import threading

#######################################____________API_REQUESTS___________________######################################

# import hashlib
import json
import requests

hashed_dic = {}
hashed_dic_grouop = {}


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

class HashedHolder:
    def __init__(self):
        self.hashed_dic_shows = {}
        self.hashed_dic_show = {}
        self.hashed_dic_movie = {}
        self.hashed_dic_movies = {}
        self.hashed_dic_search = {}

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

        # print(self._url_prepared)
        return requests.get(self._url_prepared)

    def get_search_by_id(self):

        self._url_prepared = self.short_url + self.query['_id']
        # print(self._url_prepared)
        return requests.get(self._url_prepared)

    def get_pages(self):
        return requests.get(self.url)


class Movies(api):
    def __init__(self, page=None, sort=None, order=None, keywords=None, _id=None, genre=None, **kwargs):
        # super(api, self).__init__(**kwargs)

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
        # super(self).__init__(**kwargs)

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
    # print('Got response: {}'.format(_response.json()))
    # print(json.dumps(_response.json(), sort_keys=True, indent=4))
    get_hashed_json_dic(hash_item(_response.json()))


# pippp = Shows().get_pages()
# pippp = Shows(_id = 'tt4209752').get_search_by_id()
# pippp = Shows(genre='animation', order='1', sort='name').get_search()
# pippp = Shows(page='1', order='1', sort='updated').get_search()
# pippp = Movies().get_pages()
# pippp = Movies(keywords='mission impossible', order='1', sort='name').get_search()
# pippp = Movies(_id = 'tt0120755').get_search_by_id()

def item_level_():
    pass


def hash_item_m(x):
    to_hash = '{}'.format(i['_id'])
    to_hash = to_hash.encode()
    hashed = SHA256.new(to_hash).hexdigest()


def hash_item(__json_in):  # requires JSON object
    # print(type(__json_in))
    __json_hashed_out = {}
    for i in __json_in:
        print(i)
        to_hash = '{}'.format(i['_id'])
        to_hash = to_hash.encode()
        hashed = SHA256.new(to_hash).hexdigest()

        populate_hashed_table(hashed, i['_id'])
        __json_hashed_out[hashed] = i

    return __json_hashed_out


def get_hashed_json_dic(__json_hashed_in):
    for i in __json_hashed_in:
        # print('>'*90)
        # Logger.info('>'*90)
        # to_hash = 'b"{}"'.format(i)
        # Logger.info('{} {} '.format(i, __json_hashed_in[i]))
        # hashlib.sha224(to_hash).hexdigest()
        # Logger.info('>'*90)
        # Logger.info('\n')
        hashed_dic_grouop[i] = __json_hashed_in[i]


def populate_hashed_table(_key, _pair):
    hashed_dic[_key] = _pair


#######################################____________API_REQUESTS___________________######################################


#######################################____________CONNECTOR___________________#########################################
class Connector:
    url = ''

    def __init__(self, **kwargs):
        # super(Connector, self).__init__(**kwargs)
        Logger.info('Connector: Initialized {}'.format(self))

        # self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.url:
            self.host = self.url
            # print(self.host)
        else:
            self.host = '192.168.0.10'
        self.port = 8000
        self.server_state = True

        self.connects(self.host, self.port)

    def connects(self, host, port, *args):
        try:
            # self.sock = socket.create_connection(source_address=(self.host, self.port))
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(3)
            self.sock.connect((host, port))
            self.receive()
        except:
            print'bla'
            self.server_state = False

            pass

    def mysend(self, msg, *args):
        totalsent = 0
        # print(self.server_state)
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
        # print(responded_msg.decode())
        if not len(responded_msg.decode()):
            # print('false')

            self.server_state = False
            try:
                self.sock.close()
            except OSError:
                # print('not able to close')
                pass
            self.connects(self.host, self.port)

        else:
            self.server_state = True
            # print('true')


#######################################____________CONNECTOR___________________#########################################


class Progression(Screen):
    progress_barr = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(Progression, self).__init__(**kwargs)
        Logger.info('Progression: Initialized {}'.format(self))

        # self.sch_event = Clock.schedule_interval(self.progression_bar, 0.09)
        self.sch_event = Clock.schedule_interval(self.progression_bar_handler, 1 / 60)

    def progression_bar_handler(self, *args):
        # Logger.info('Progression: Progress Bar progress {}'.format(self.ids.pb.value))

        # print(self.ids.zz.size_hint_x)
        if self.ids.pb.value < 100:
            self.ids.pb.value += 1  # add value to progress bar
            # self.ids.dynamic_progress.size_hint_x += 0.01
            # self.ids.static_progress.size_hint_x -= 0.01
            # self.ids.dv.size_hint_x -= 0.01
            self.ids.dv.opacity -= 0.01  # fade out overlay
            self.ids.dd.opacity += 0.01  # fade in main image
        else:
            Logger.info('Progression: Progress bar scheduler event stopped')

            self.sch_event.cancel()

            self.manager.switch_to(ScanView(), transition=FadeTransition(), duration=1)


class MoviesView(Screen):
    def __init__(self, **kwargs):
        super(MoviesView, self).__init__(**kwargs)
        Logger.info('MoviesView: Initialized {}'.format(self))
        Clock.schedule_once(self.pr, 9)

    def set_to_cur(self, scn, *args):
        self.manager.current = scn

    def pr(self, *args):
        # print(self.parent)
        # print(self.manager.screens)
        # print(' MainView {}'.format(self.parent))
        # print(self.manager.screen_names)
        pass

    pass


class Item(BoxLayout):
    def __init__(self, sname, **kwargs):
        super(Item, self).__init__(**kwargs)
        Logger.info('Item: Initialized {}'.format(self))
        self.megs = sname
        self.popup = Popup(title='Test popup',
                           content=Label(text=self.megs),
                           size_hint=(None, None), size=(600, 600))
        self.add_widget(Button(text='show', on_release=self.oppop, size_hint_y=.1))

    def oppop(self, *args):
        self.popup.open()


class SeriesView(Screen):
    def __init__(self, **kwargs):
        super(SeriesView, self).__init__(**kwargs)
        Logger.info('SeriesView: Initialized {}'.format(self))
        Logger.info('This is window size {}'.format(Window.size))
        Logger.info('This is container size {}'.format(self.size))

        Clock.schedule_once(self.pr, 9)

        layout = GridLayout(cols=3, padding=50, spacing=50,
                            size_hint=(None, None), width=ViewControl.width_x - 30)

        # when we add children to the grid layout, its size doesn't change at
        # all. we need to ensure that the height will be the minimum required
        # to contain all the childs. (otherwise, we'll child outside the
        # bounding box of the childs)
        layout.bind(minimum_height=layout.setter('height'))

        oooo = ScrollView(size_hint=(None, None), size=(ViewControl.width_x - 20, ViewControl.height_x - 150),
                          pos_hint={'center_x': .5, 'center_y': .5}, do_scroll_x=False)
        oooo.add_widget(layout)
        # print(self.ids)
        self.ids.series_view_container.add_widget(oooo)

        # pippp = Shows(genre='animation', order='1', sort='name').get_search()
        # check_api_validity(pippp)
        # Logger.info(json.dumps(pippp.json(), sort_keys=True, indent=4))

        # _items = Item()
        # _items.add_widget(AsyncImage(source=hashed_dic_grouop['6b43cd1e32c32983ff0b1a520812ecc7b008c32097ead5812168d33967246151']['images']['poster']))
        # self.add_widget(_items)
        for kk in hashed_dic_grouop:
            #     print('{}----{}'.format(kk, hashed_dic_grouop[kk]))
            _items = Item(hashed_dic_grouop[kk]['_id'])
            _items.size = ((Window.size[0] / 3) - 80, (Window.size[1] / 2) - 30)
            try:
                _items.add_widget(AsyncImage(source=hashed_dic_grouop[kk]['images']['poster'], nocache=True))
            except KeyError:
                Logger.info('No image setting default')
                _items.add_widget(Image(source='images/logo.png'))
            _items.add_widget(Label(text=hashed_dic_grouop[kk]['title'], size_hint_y=.1))

            layout.add_widget(_items)
        #     _items.add_widget(Label(text=hashed_dic_grouop[kk]['title']))
        #
        #
        #     layout.add_widget(_items)
        #     """{'_id': 'tt3793630', 'imdb_id': 'tt3793630', 'tvdb_id': '282756', 'title': 'The Lion Guard', 'year': '2016', 'slug': 'the-lion-guard', 'rating': {'percentage': 68, 'watching': 0, 'votes': 42, 'loved': 100, 'hated': 100}, 'num_seasons': 2, 'images': {'poster': 'http://image.tmdb.org/t/p/w500/AtDL8ZrOZxW1jakT2R3LcMdLvQD.jpg', 'fanart': 'http://image.tmdb.org/t/p/w500/6nArW4w8UVJyElJpgS7f1MuO3QO.jpg', 'banner': 'http://image.tmdb.org/t/p/w500/AtDL8ZrOZxW1jakT2R3LcMdLvQD.jpg'}}"""
        #     self.thr = threading.Thread(target=self.get_u, args=(kk,))
        #     self.thr.start()
        # self.get_u(kk)
        # for line in q.stdout:
        #     l += 1
        #     # print(line)
        #     layout.add_widget(
        #         Label(text=str(line[32:]), size=(690, 40), size_hint=(None, None), font_size=12, color=[0, 0.31, 0, 1]))
        #
        #     # Clock.schedule_interval(partial(self.up_t, line), 1)
        #     # if l == 10:
        #
        #     #     print("\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        #     if l > 1:
        #         break

    def set_to_cur(self, scn, *args):
        self.manager.current = scn

    def pr(self, *args):
        # print(self.parent)
        # print(self.manager.screens)
        # print(' MainView {}'.format(self.parent))
        # print(self.manager.screen_names)
        pass

    pass


class SearchView(Screen):
    def __init__(self, **kwargs):
        super(SearchView, self).__init__(**kwargs)
        Logger.info('SearchView: Initialized {}'.format(self))
        # print(self.ids)

    def set_to_cur(self, scn, *args):
        self.manager.current = scn

        Clock.schedule_once(self.pr, 9)

    def pr(self, *args):
        # print(self.parent)
        # print(self.manager.screens)
        # print(' MainView {}'.format(self.parent))
        # print(self.manager.screen_names)
        pass

    pass


class LatestView(Screen):
    def __init__(self, **kwargs):
        super(LatestView, self).__init__(**kwargs)
        Logger.info('LatestView: Initialized {}'.format(self))
        # print(self.ids)

        Clock.schedule_once(self.pr, 9)

        self.connn = Connector()

    def set_to_cur(self, scn, *args):
        self.manager.current = scn

    def cc(self, msg, *args):
        self.connn.mysend(msg)

    def reconnect(self, *args):
        self.connn.connects(self.connn.host, self.connn.port)

    def pr(self, *args):
        # print(self.parent)
        # print(self.manager.screens)
        # print(' MainView {}'.format(self.parent))
        # print(self.manager.screen_names)
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


class MainView(Screen):
    def __init__(self, **kwargs):
        super(MainView, self).__init__(**kwargs)
        Logger.info('MainView: Initialized {}'.format(self))
        # Clock.schedule_once(self.pr, 9)
        self.scm = MainViewScManager()
        self.ids.screen_m_container.add_widget(self.scm)
        # print(self.ids)

    def set_to_cur(self, scn, *args):
        self.scm.current = scn

    def pr(self, *args):
        # print(self.parent)
        # print(self.manager.screens)
        # print(' MainView {}'.format(self.parent))
        # print(self.manager.screen_names)
        if 'settings' not in self.manager.screen_names:

            self.manager.switch_to(SettingsView(), transition=FadeTransition())
        else:
            self.manager.current = 'settings'

    pass


class ScanView(Screen):
    urls_list = {}

    def __init__(self, **kwargs):
        super(ScanView, self).__init__(**kwargs)
        Logger.info('ScanView: Initialized {}'.format(self))

        self._urls_list = self.urls_list
        for it in self._urls_list:
            # print(it)
            self.ids.scan_view_container.add_widget(
                Button(text='{}/{}'.format(it, self._urls_list[it]), on_press=self.set_as_host))

        #################################_________________API_IMPL__________________________####################################

        self.start_service()

    def start_service(self, *args):
        # pippp = Shows(order='1', sort='name').get_search()
        pippp = Shows(_id='tt4209752').get_search_by_id()

        # pippp = Movies(order='1', sort='name').get_search()
        api_request_handler(pippp)
        # Logger.info(json.dumps(pippp.json(), sort_keys=True, indent=4))

        # for kk in hashed_dic_grouop:
        #     self.thr = threading.Thread(target=self.get_u, args=(kk,))
        #     self.thr.start()
        # self.get_u(kk)

        # for i in hashed_dic:
        #     print('{} {} '.format(i, hashed_dic[i]))

    def get_u(self, vz, *args):
        Logger.info(hashed_dic[vz])
        pipd = Shows(_id=hashed_dic[vz]).get_search_by_id()
        Logger.info(json.dumps(pipd.json(), sort_keys=True, indent=4))

    #################################_________________API_IMPL__________________________####################################

    def set_as_host(parent, instance):
        breaker = instance.text.find('/')
        prepare_url = instance.text[:breaker]
        # print(prepare_url)
        Connector.url = prepare_url

    def pr(self, *args):
        # print(self.parent)
        # print(self.manager.screens)
        self.manager.switch_to(MainView(), transition=FadeTransition(), duration=1)


class SettingsView(Screen):
    def __init__(self, **kwargs):
        super(SettingsView, self).__init__(**kwargs)
        Logger.info('SettingsView: Initialized {}'.format(self))
        Clock.schedule_once(self.pr, 9)

    def pr(self, *args):
        # print(self.parent)
        # print(self.manager.screens)
        self.manager.current = 'main'
        # print(' MainView {}'.format(self.parent))


class So:
    def __init__(self, **kwargs):
        Logger.info('So: Initialized {}'.format(self))

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(2)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


class ViewControl(ScreenManager):
    # print(Window.size)
    height_x = Window.size[1]
    width_x = Window.size[0]

    def __init__(self, **kwargs):
        super(ViewControl, self).__init__(**kwargs)
        Logger.info('ViewControl: Initialized {}'.format(self))

        self.t1 = threading.Thread(name="Loading screen", target=self.init_loading_screen())
        self.t1.start()

        for _subnet in range(9, 13):
            self.t2 = threading.Thread(target=self.scan_network, args=(_subnet,))
            self.t2.start()

    def init_loading_screen(self, *args):
        self.add_widget(Progression(name='loading'))

    def scan_network(self, _subnet, *args):
        # Logger.info('entered scanner for {}'.format(threading.currentThread().getName()))

        network = '192.168.0.{}'.format(_subnet)
        Logger.info('Scanner for {}'.format(network))
        # network = '10.85.180.{}'.format(_subnet)
        s = So()

        try:
            _socket = s.sock.connect_ex((network, 8000))

            if _socket == 0:
                Logger.info('Found online at {}'.format(network))

                responded_msgs = s.sock.recv(2048)
                ScanView.urls_list[network] = str(responded_msgs.decode())
                s.sock.close()

            else:
                Logger.info('{} responded {}'.format(network, _socket))

        finally:
            s.sock.close()
            Logger.info('Current :{} Exiting for {}'.format(threading.currentThread().getName(), _subnet))


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


