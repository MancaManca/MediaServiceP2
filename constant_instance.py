from collections import OrderedDict
from kivy import Logger
from kivy.core.window import Window
from kivy.animation import Animation

from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import FadeTransition
from kivy.uix.scrollview import ScrollView
import socket
from plex import Plex

height_x = Window.size[1]
width_x = Window.size[0]
w_l_start = 0
w_l_stop = 7
animation_interval = .05
animation_height_decrese = 20
pr_speed = 1/60
navigation_buttons = OrderedDict()
navigation_buttons['Movies'] = 'movies_view'
navigation_buttons['Series'] = 'series_view'
navigation_buttons['Latest'] = 'latest_view'
navigation_buttons['Favourites'] = 'favourites_view'
TRANSITION = FadeTransition
UNIQUE_V_W = 20
LAT_V_H = 0.4
FAV_V_H = 0.88
SHO_V_H = 0.835
ITEM_ANIM_DUR = 1.0
ITEM_A_W = (width_x / 3) - 30
ITEM_A_H = (height_x / 2) - 300
CACHE_TIME = 20

sm_anim_time = 0.7


class ScrollGrid(GridLayout):

    def __init__(self, **kwargs):
        super(ScrollGrid, self).__init__(**kwargs)
        Logger.info('ScrollGrid: Initialized {}'.format(self))
        self.cols = 3
        self.padding = 25
        self.spacing = 15
        self.size_hint = (None, None)
        self.width = width_x - 30


class ScrollGridHorizontal(GridLayout):

    def __init__(self, cols=None, **kwargs):
        super(ScrollGridHorizontal, self).__init__(**kwargs)
        Logger.info('ScrollGridHorizontal: Initialized {}'.format(self))
        if cols:
            self.cols = cols
        else:
            self.cols = 50
        self.rows = 1
        self.padding = 5
        self.spacing = 5
        self.size_hint = (None, None)


class ScrollV(ScrollView):
    def __init__(self, scroll_w, scroll_h, on_scroll_a=None, on_scroll_ar=None, **kwargs):
        super(ScrollV, self).__init__(**kwargs)
        Logger.info('ScrollV: Initialized {} width {} height {}'.format(self, str(scroll_w), str(scroll_h)))
        self.size_hint = (None, None)
        self.size = (width_x - scroll_w, height_x * scroll_h)
        self.pos_hint = {'center_x': 0.5, 'center_y': .5}
        self.do_scroll_x = False
        if on_scroll_a:
            self.on_scroll_move = lambda x: on_scroll_a(self, on_scroll_ar)


class ScrollVHorizontal(ScrollView):
    def __init__(self, **kwargs):
        super(ScrollVHorizontal, self).__init__(**kwargs)
        Logger.info('ScrollVHorizontal: Initialized ')
        self.size_hint = (1, 1)
        self.do_scroll_x = True
        self.do_scroll_y = False
        self.bar_color = [0,0,0,0]
        self.bar_inactive_color = [0,0,0,0]


class ItemAnimation(Animation):
    def __init__(self, **kwargs):
        super().__init__(size=(ITEM_A_W, ITEM_A_H), duration=ITEM_ANIM_DUR)



class So:
    def __init__(self, **kwargs):
        Logger.info('So: Initialized {}'.format(self))

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(2)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


class Connector:
    url = ''

    def __init__(self, **kwargs):
        Logger.info('Connector: Initialized {}'.format(self))
        self.plex_inst = Plex()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.url = self.plex_inst.get_stored_server()[1]
        except KeyError:
            self.url = None
            pass

        if self.url:
            self.host = self.url
        else:
            self.host = None
        self.port = 8000
        self.server_state = True
        self.connects(self.host, self.port)
        self.device_response = ''

    def connects(self, host, port, *args):
        try:
            self.sock.settimeout(3)
            self.sock.connect((host, port))
            self.receive()
            Logger.info('Connected to host {}'.format(host))

        except Exception as e:
            Logger.warning('No connection to device due to {}'.format(e))

            self.server_state = False
            pass

    def mysend(self, msg, *args):
        if self.server_state:
            try:
                self.sock.send(b'{}'.format(msg))
                self.receive()
                return self.device_response
            except Exception as e:
                return 'fail'

                pass
        else:
            Logger.info('No connection to device')
            return 'fail'

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
                Logger.warning('not able to close')

                pass
            self.device_response = 'fail'
            self.connects(self.host, self.port)

        else:
            self.server_state = True
            Logger.info('device connection sucess')
            Logger.warning('Connector: Device responded with message {}'.format(responded_msg.decode()))
            self.device_response = responded_msg.decode()


