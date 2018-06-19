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

hashed_dic_shows = {}
hashed_dic_show = {}
hashed_dic_movie = {}
hashed_dic_movies = {}
hashed_dic_search = {}

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
    # print(type(__json_in))
    __json_hashed_out = {}
    if method_flag:
        print('going for multi flag {}'.format(method_flag))
        for i in __json_in:
            hashed = hash_item_m(i['_id'])
            __json_hashed_out[hashed] = i
    else:
        print('going for multi flag {}'.format(method_flag))
        hashed = hash_item_m(__json_in['_id'])
        __json_hashed_out[hashed] = __json_in



    return __json_hashed_out

def populate_hashed_json_dic(__json_hashed_in, to_dic):

    to_dic.clear()
    for i in __json_hashed_in:
        to_dic[i] = __json_hashed_in[i]
    print('populated dic')
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
    print(_api_call.url)

    try:
        api_request_handler(_api_call)
        api_request_controler(_api_call)
    except Exception as e:
        print(e)
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
            self.sock.connect((host,port))
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
        self.sch_event = Clock.schedule_interval(self.progression_bar_handler, 1/60)

    def progression_bar_handler(self, *args):
        # Logger.info('Progression: Progress Bar progress {}'.format(self.ids.pb.value))

        # print(self.ids.zz.size_hint_x)
        if self.ids.pb.value < 100:
            self.ids.pb.value += 1 #add value to progress bar
            # self.ids.dynamic_progress.size_hint_x += 0.01
            # self.ids.static_progress.size_hint_x -= 0.01
            # self.ids.dv.size_hint_x -= 0.01
            self.ids.dv.opacity -= 0.01 # fade out overlay
            self.ids.dd.opacity += 0.01 # fade in main image
        else:
            Logger.info('Progression: Progress bar scheduler event stopped')

            self.sch_event.cancel()

            self.manager.switch_to(ScanView(),transition=FadeTransition(), duration=1)


class MoviesViewMainSingle(Screen):
    def __init__(self, movie_id, **kwargs):
        super(MoviesViewMainSingle, self).__init__(**kwargs)
        self.movie_id = movie_id
        self.name = 'mvms'
        self.blak = self
        Logger.info('MoviesViewMainSingle: Initialized {}'.format(self))
        self.ids.mvmsingle.add_widget(Label(text=self.name))
        self.ids.mvmsingle.add_widget(Button(text='back',on_press = self.go_back_to_movies))
        get_api(Movies(_id = self.movie_id).get_search_by_id())
        for i in hashed_dic_movie:
            print(i)
            for b in hashed_dic_movie[i]:
                print(b)
                self.ids.mvmsingle.add_widget(Label(text=b))



    def go_back_to_movies(self,*args):
        self.manager.current = 'movies view main screen'
        self.manager.remove_widget(self.blak)
    # def change_to_movies_single

class MoviesViewMain(Screen):
    def __init__(self, **kwargs):
        super(MoviesViewMain, self).__init__(**kwargs)
        Logger.info('MoviesViewMain: Initialized {}'.format(self))
        self.name = 'movies view main screen'
        self.add_widget(Button(text='go to single movie',on_press = self.change_to_movies_single,size_hint_y=0.1))

        movies_layout = GridLayout(cols=3, padding=50, spacing=50,
                            size_hint=(None, None), width=ViewControl.width_x - 30)

        # when we add children to the grid layout, its size doesn't change at
        # all. we need to ensure that the height will be the minimum required
        # to contain all the childs. (otherwise, we'll child outside the
        # bounding box of the childs)
        movies_layout.bind(minimum_height=movies_layout.setter('height'))

        movies_scroll_list = ScrollView(size_hint=(None, None), size=(ViewControl.width_x - 20, ViewControl.height_x - 190),
                          pos_hint={'center_x': .5, 'center_y': .5}, do_scroll_x=False)
        movies_scroll_list.add_widget(movies_layout)
        # print(self.ids)
        self.ids.movies_view_main_container.add_widget(movies_scroll_list)

        # pippp = Shows(genre='animation', order='1', sort='name').get_search()
        # check_api_validity(pippp)
        # Logger.info(json.dumps(pippp.json(), sort_keys=True, indent=4))

        # _items = Item()
        # _items.add_widget(AsyncImage(source=hashed_dic_grouop['6b43cd1e32c32983ff0b1a520812ecc7b008c32097ead5812168d33967246151']['images']['poster']))
        # self.add_widget(_items)
        for kk in hashed_dic_movies:
            #     print('{}----{}'.format(kk, hashed_dic_grouop[kk]))
            _items = Item(hashed_dic_movies[kk]['_id'])
            _items.size = ((Window.size[0] / 3) - 80, (Window.size[1] / 2) - 30)
            try:
                _items.add_widget(AsyncImage(source=hashed_dic_movies[kk]['images']['poster'], nocache=True))
            except Exception as e:
                pass
                Logger.info('No image setting default cause of {}'.format(e))
                _items.add_widget(Image(source='images/logo.png'))
            _items.add_widget(Label(text=hashed_dic_movies[kk]['title'], size_hint_y=.1,text_size=(250, None),shorten_from='right',halign='center',shorten=True))
            _items.add_widget(Button(text = 'show',on_press = lambda x: self.change_to_movies_single(hashed_dic_movies[kk]['_id'])))

            movies_layout.add_widget(_items)


    def change_to_movies_single(self, x,*args):
        print(self.manager)

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

        self.add_widget(ScMaMovies())
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
    def __init__(self,sname, **kwargs):
        super(Item, self).__init__(**kwargs)
        Logger.info('Item: Initialized {}'.format(self))
        self.megs = sname
        print(self.megs)
        self.popup = Popup(title='Test popup',
                      content=Label(text=self.megs),
                      size_hint=(None, None), size=(600, 600))
        # self.add_widget(Button(text='show',on_release=self.change_to_movies_single,size_hint_y=.1))
    def oppop(self, *args):

        self.popup.open()

    def change_to_movies_single(self,*args):
        print(ScMaMovies)

        ScMaMovies.add_widget(MoviesViewMainSingle(self.megs))
        ScMaMovies.current = 'mvms'

class SeriesView(Screen):
    def __init__(self, **kwargs):
        super(SeriesView, self).__init__(**kwargs)
        Logger.info('SeriesView: Initialized {}'.format(self))
        Logger.info('This is window size {}'.format(Window.size))
        Logger.info('This is container size {}'.format(self.size))



        Clock.schedule_once(self.pr, 9)

        shows_layout = GridLayout(cols=3, padding=50, spacing=50,
                            size_hint=(None, None), width=ViewControl.width_x-30)

        # when we add children to the grid layout, its size doesn't change at
        # all. we need to ensure that the height will be the minimum required
        # to contain all the childs. (otherwise, we'll child outside the
        # bounding box of the childs)
        shows_layout.bind(minimum_height=shows_layout.setter('height'))

        shows_scroll_list = ScrollView(size_hint=(None, None), size=(ViewControl.width_x-20, ViewControl.height_x-190),
                          pos_hint={'center_x': .5, 'center_y': .5}, do_scroll_x=False)
        shows_scroll_list.add_widget(shows_layout)
        # print(self.ids)
        self.ids.series_view_container.add_widget(shows_scroll_list)

        # pippp = Shows(genre='animation', order='1', sort='name').get_search()
        # check_api_validity(pippp)
        # Logger.info(json.dumps(pippp.json(), sort_keys=True, indent=4))


        # _items = Item()
        # _items.add_widget(AsyncImage(source=hashed_dic_grouop['6b43cd1e32c32983ff0b1a520812ecc7b008c32097ead5812168d33967246151']['images']['poster']))
        # self.add_widget(_items)
        for kk in hashed_dic_shows:
        #     print('{}----{}'.format(kk, hashed_dic_grouop[kk]))
            _items = Item(hashed_dic_shows[kk]['_id'])
            _items.size = ((Window.size[0]/3)-80,(Window.size[1]/2)-30)
            try:
                _items.add_widget(AsyncImage(source=hashed_dic_shows[kk]['images']['poster'],nocache=True))
            except Exception as e:
                pass
                Logger.info('No image setting default cause of {}'.format(e))
                _items.add_widget(Image(source='images/logo.png'))
            _items.add_widget(Label(text=hashed_dic_shows[kk]['title'],size_hint_y=.1))

            shows_layout.add_widget(_items)
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
        self.connn.connects(self.connn.host,self.connn.port)

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
        if 'settings' not  in self.manager.screen_names:

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
            self.ids.scan_view_container.add_widget(Button(text='{}/{}'.format(it, self._urls_list[it]), on_press=self.set_as_host))

#################################_________________API_IMPL__________________________####################################

        self.start_service()


    def start_service(self, *args):
        # pippp = Shows(order='1', sort='name').get_search()
        """get inital latest movies and series, populate shows dictionary populate movies dicionary"""
        get_api(Shows(order='-1', sort='name').get_search())
        get_api(Movies(order='-1', sort='name').get_search())
        """"""
        # pippp = Shows(_id = 'tt4209752').get_search_by_id()

        # pippp = Movies(order='1', sort='name').get_search()
        # api_request_handler(pippp)
        # Logger.info(json.dumps(pippp.json(), sort_keys=True, indent=4))

        # for kk in hashed_dic_grouop:
        #     self.thr = threading.Thread(target=self.get_u, args=(kk,))
        #     self.thr.start()
            # self.get_u(kk)

        # for i in hashed_dic:
        #     print('{} {} '.format(i, hashed_dic[i]))

    # def get_u(self, vz, *args):
    #
    #     Logger.info(hashed_dic[vz])
    #     pipd = Shows(_id=hashed_dic[vz]).get_search_by_id()
    #     Logger.info(json.dumps(pipd.json(), sort_keys=True, indent=4))

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

        for _subnet in range(9,13):

            self.t2 = threading.Thread(target=self.scan_network, args=(_subnet,))
            self.t2.start()

    def init_loading_screen(self, *args):
        self.add_widget(Progression(name='loading'))

    def scan_network(self ,_subnet, *args):
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
            Logger.info('Current :{} Exiting for {}'.format(threading.currentThread().getName(),_subnet))


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

