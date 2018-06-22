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
from kivy.uix.modalview import ModalView
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.scrollview import ScrollView

from kivy.utils import get_color_from_hex
from Crypto.Hash import SHA256


import socket
import threading

#######################################____________API_REQUESTS___________________######################################

import requests

hashed_dic_shows = {}
hashed_dic_show = {}
hashed_dic_movie = {}
hashed_dic_movies = {}
hashed_dic_search = {}
scanned_online_urls = {}

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
            self.host = '192.168.0.10'
        self.port = 8000
        self.server_state = True
        self.connects(self.host, self.port)

    def connects(self, host, port, *args):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(3)
            self.sock.connect((host,port))
            self.receive()
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
        get_api(Movies(_id = self.movie_id).get_search_by_id())
        for i in hashed_dic_movie:
            for b in hashed_dic_movie[i]:
                self.ids.mvmsingle.add_widget(Label(text=b))



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

        movies_scroll_list = ScrollView(size_hint=(None, None), size=(ViewControl.width_x - 20, ViewControl.height_x/1.5 - 50),
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


        self.paginator = GridLayout(rows=1,cols=5,padding=5, spacing=5)
        for i in range(1,5):
            btn = Button(text=str(i),on_press=lambda instance: self.set_p(instance))
            self.paginator.add_widget(btn)
        self.ids.pag_holder.add_widget(self.paginator)

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
        get_api(Movies(page=num.text,inorder='-1', sort='name').get_search())

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

        shows_scroll_list = ScrollView(size_hint=(None, None), size=(ViewControl.width_x-20, ViewControl.height_x-300),
                          pos_hint={'center_x': .5, 'center_y': .5}, do_scroll_x=False)
        shows_scroll_list.add_widget(shows_layout)
        # Logger.info(self.ids)
        self.ids.series_view_container.add_widget(shows_scroll_list)

        # pippp = Shows(genre='animation', order='1', sort='name').get_search()
        # check_api_validity(pippp)
        # Logger.info(json.dumps(pippp.json(), sort_keys=True, indent=4))

        for kk in hashed_dic_shows:
        # Logger.info('{}----{}'.format(kk, hashed_dic_grouop[kk]))
            _items = Item(hashed_dic_shows[kk]['_id'])
            _items.size = ((Window.size[0]/3)-80,(Window.size[1]/2)-80)
            try:
                _items.add_widget(AsyncImage(source=hashed_dic_shows[kk]['images']['poster'],nocache=True))
            except Exception as e:
                pass
                Logger.info('No image setting default cause of {}'.format(e))
                _items.add_widget(Image(source='images/logo.png'))
            _items.add_widget(Label(text=hashed_dic_shows[kk]['title'],size_hint_y=.1))

            shows_layout.add_widget(_items)
        #
        #
        #     """{'_id': 'tt3793630', 'imdb_id': 'tt3793630', 'tvdb_id': '282756', 'title': 'The Lion Guard', 'year': '2016', 'slug': 'the-lion-guard', 'rating': {'percentage': 68, 'watching': 0, 'votes': 42, 'loved': 100, 'hated': 100}, 'num_seasons': 2, 'images': {'poster': 'http://image.tmdb.org/t/p/w500/AtDL8ZrOZxW1jakT2R3LcMdLvQD.jpg', 'fanart': 'http://image.tmdb.org/t/p/w500/6nArW4w8UVJyElJpgS7f1MuO3QO.jpg', 'banner': 'http://image.tmdb.org/t/p/w500/AtDL8ZrOZxW1jakT2R3LcMdLvQD.jpg'}}"""
        #
    def set_to_cur(self, scn, *args):
        self.manager.current = scn
    def pr(self, *args):
        # Logger.info(self.parent)
        # Logger.info(self.manager.screens)
        # Logger.info(' MainView {}'.format(self.parent))
        # Logger.info(self.manager.screen_names)
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
    def set_to_cur(self, scn, *args):
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

class MainView(Screen):
    def __init__(self, **kwargs):
        super(MainView, self).__init__(**kwargs)
        Logger.info('MainView: Initialized {}'.format(self))
        # Clock.schedule_once(self.pr, 9)
        self.scm = MainViewScManager()
        self.ids.screen_m_container.add_widget(self.scm)
        # Logger.info(self.ids)

        self.view = ModalView(auto_dismiss=True,size_hint=(None, None), size=(Window.size[0]/2, Window.size[1]/2))
        self.view.add_widget(Label(text='Hello world'))
    def op_m(self, *args):
        self.view.open()
    def set_to_cur(self, scn, *args):
        self.scm.current = scn
    def pr(self, *args):
        # Logger.info(self.parent)
        # Logger.info(self.manager.screens)
        # Logger.info(' MainView {}'.format(self.parent))
        # Logger.info(self.manager.screen_names)
        if 'settings' not  in self.manager.screen_names:

            self.manager.switch_to(SettingsView(), transition=FadeTransition())
        else:
            self.manager.current = 'settings'

    pass

class ScanView(Screen):

    def __init__(self, **kwargs):
        super(ScanView, self).__init__(**kwargs)
        Logger.info('ScanView: Initialized {}'.format(self))

        self._urls_list = scanned_online_urls

        for it in self._urls_list:
            # Logger.info(it)
            self.ids.scanned_devices_list.add_widget(Button(text='{}/{}'.format(it, self._urls_list[it]), on_press=self.set_as_host))

#################################_________________API_IMPL__________________________####################################

        self.start_service()


    def start_service(self, *args):
        # pippp = Shows(order='1', sort='name').get_search()
        """get inital latest movies and series, populate shows dictionary populate movies dicionary"""
        get_api(Shows(order='-1', sort='name').get_search())
        get_api(Movies(order='-1', sort='name').get_search())
        """"""


#################################_________________API_IMPL__________________________####################################

    def set_as_host(parent, instance):
        breaker = instance.text.find('/')
        prepare_url = instance.text[:breaker]
        # Logger.info(prepare_url)
        Connector.url = prepare_url

    def pr(self, *args):
        # Logger.info(self.parent)
        # Logger.info(self.manager.screens)
        self.manager.switch_to(MainView(), transition=FadeTransition(), duration=1)



class SettingsView(Screen):
    def __init__(self, **kwargs):
        super(SettingsView, self).__init__(**kwargs)
        Logger.info('SettingsView: Initialized {}'.format(self))

        self.settings_scanned_devices = scanned_online_urls

        Clock.schedule_once(self.return_to_main_view, 9)
        self.update_list_devices()

    def scan_again(self, *args):
        # ViewControl.start_scanning()
        Clock.schedule_once(self.update_list_devices, 9)
    def update_list_devices(self, *args):
        self.ids.settings_view_container_list_container.clear_widgets()
        for i in self.settings_scanned_devices:
            self.ids.settings_view_container_list_container.add_widget(Label(text=self.settings_scanned_devices[i]))
    def return_to_main_view(self, *args):
        # Logger.info(self.parent)
        # Logger.info(self.manager.screens)
        self.manager.current = 'main'
        # Logger.info(' MainView {}'.format(self.parent))

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

        self.sch_event = Clock.schedule_interval(self.progression_bar_handler, 0.08)

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

        self.start_scanning()

    def scan_network_for_single_connection(self, _subnet):
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

    def start_scanning(self, *args):
        for _subnet_in in range(9,13):
            self.t2 = threading.Thread(target=self.scan_network_for_single_connection, args=(_subnet_in,))
            self.t2.start()

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

