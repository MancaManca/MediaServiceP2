from kivy.app import App
from kivy.animation import Animation
from kivy.cache import Cache
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics.vertex_instructions import Rectangle
from kivy.metrics import dp
from kivy.properties import ObjectProperty, BooleanProperty, StringProperty, partial
from kivy.uix.accordion import Accordion, AccordionItem
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition, SlideTransition, CardTransition, SwapTransition, WipeTransition, RiseInTransition
from kivy.uix.scrollview import ScrollView
from kivy.uix.stencilview import StencilView
from kivy.uix.togglebutton import ToggleButton
from kivy.utils import get_color_from_hex
from kivy import Logger
from Crypto import Random
from Crypto.Cipher import AES

import constant_instance as c_i
import util_f
from api import Movies, Shows, hash_item_m

# TRANSITION = FadeTransition
from db import Media, Filter, Favourites, Network
from plex import Plex
from util import scan_network_for_single_connection

# scanned_online_urls = OrderedDict()
# chosen_scanned_url = ''

##### COLOR PALET #####

YELLOW = get_color_from_hex('#FFBA1B')
GRAY = get_color_from_hex('#212121')
BLACK = get_color_from_hex('#000000')
WHITE = get_color_from_hex('#ffffff')

##### COLOR PALET #####




class SingleTor(BoxLayout):

    def __init__(self, _torrent_single, _torrent_single_magnet, _connector, **kwargs):
        super(SingleTor, self).__init__(**kwargs)
        Logger.info('SingleTor: Initialized {}'.format(self))

        self.wtf = _connector

        self._torrent_quality = str(_torrent_single)
        self._torrent_quality = self._torrent_quality.encode('utf-8')
        self.ids.tor_quality_label.text = str(self._torrent_quality)
        self._magnet_link = str(_torrent_single_magnet)
        self._magnet_link = self._magnet_link.encode('utf-8')
        self.play = 'play/{}'.format(self._magnet_link)
        self.download = 'down/{}'.format(self._magnet_link)
        self.ckey = '0123456789111315'
        self.iv = Random.new().read(AES.block_size)
        Logger.warning('single tor : iv is ---- "{}" and the length is {}'.format(self.iv, len(self.iv)))
        self.cipher = AES.new(self.ckey, AES.MODE_CFB, self.iv)
        self.ciphertext = self.cipher.encrypt(self.download)
        Logger.warning('single tor : cipher {}'.format(self.ciphertext))


    def play_torrent(self, *args):
        self.informer = self.wtf.mysend(self.play)

        Logger.warning('Trying: should be message "{}" '.format(self.play))
        Logger.warning('Device response to request: "{}" '.format(self.informer))

        util_f.command_status_info(0, 3, self.informer)

    def download_torrent(self, *args):
        Logger.warning(len(self.iv))
        Logger.warning(self.iv)

        self.informer = self.wtf.mysend(self.ciphertext+self.iv)
        Logger.warning('Trying: should be message "{}" '.format(self.ciphertext))
        Logger.warning('Device response to request: "{}" '.format(self.informer))

        util_f.command_status_info(0, 3, self.informer)


class Tor(BoxLayout):

    def __init__(self, _torrents_list, _connector, **kwargs):
        super(Tor, self).__init__(**kwargs)
        Logger.info('Tor:  Initialized {}'.format(self))
        Logger.info('Tor:  torrents list {}'.format(_torrents_list))

        for _torrent in _torrents_list:
            Logger.info('Tor:  torrent {}'.format(_torrent))

            try:
                _mag_link = _torrents_list[_torrent]['url']
                self.add_widget(SingleTor(_torrent, _mag_link, _connector))
            except TypeError:
                Logger.warning('Tor: torrent missing {}'.format(_torrent))
                pass


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
        self.movies_single_connector = c_i.Connector()

        self.movie_id = movie_id
        self.name = 'mvms'
        self.movies_main_single_screen_instance = self

        Logger.info('MoviesViewMainSingle: Initialized {} for {}'.format(self.name, movie_id))
        # print ViewControl.d_data['hashed_dic_movie']['val']

        hashed_dic_movie = ViewControl.d_data['hashed_dic_movie']['val']
        # print hashed_dic_movie
        for _single_movie_item_in_dic in hashed_dic_movie:

            Logger.info('Movie level >>>>>')

            Logger.info('MoviesViewMainSingle: Movie title {}'.format(hashed_dic_movie[_single_movie_item_in_dic]['title']))
            _movie_t = str(hashed_dic_movie[_single_movie_item_in_dic]['title'])
            _movie_t = _movie_t.encode('utf-8')
            self.ids.movies_view_main_single_nav_title_t.text = _movie_t

            Logger.info('MoviesViewMainSingle: Movie year {}'.format(hashed_dic_movie[_single_movie_item_in_dic]['year']))
            _movie_y = str(hashed_dic_movie[_single_movie_item_in_dic]['year'])
            _movie_y = _movie_y.encode('utf-8')


            _movie_s = hashed_dic_movie[_single_movie_item_in_dic]['synopsis']
            _movie_s = _movie_s.encode('utf-8')
            Logger.info('MoviesViewMainSingle: Movie synopsis {}'.format(_movie_s))

            Logger.info('MoviesViewMainSingle: Movie runtime {}'.format(hashed_dic_movie[_single_movie_item_in_dic]['runtime']))
            _movie_r = str(hashed_dic_movie[_single_movie_item_in_dic]['runtime'])
            _movie_r = _movie_r.encode('utf-8')

            try:
                Logger.info('MoviesViewMainSingle: Movie image {}'.format(hashed_dic_movie[_single_movie_item_in_dic]['images']['poster'].replace('https', 'http')))
                _movie_im = str(hashed_dic_movie[_single_movie_item_in_dic]['images']['poster'])
                _movie_im = _movie_im.encode('utf-8')
                _movie_im = _movie_im.replace('https', 'http')
            except KeyError:
                Logger.warning('MoviesViewMainSingle: Movie image fallback')
                _movie_im = './images/logo.png'
                pass

            self.movie_torr_num = len(hashed_dic_movie[_single_movie_item_in_dic]['torrents']['en'])
            Logger.info('MoviesViewMainSingle: Movie number of torrents {}'.format(self.movie_torr_num))

            self.ids.movies_view_main_single_container.add_widget(
                MoviesViewMainSingleTop(_movie_y, _movie_s, _movie_r, _movie_im))

            self.ids.movies_view_main_single_container_se.add_widget(Tor(hashed_dic_movie[_single_movie_item_in_dic]['torrents']['en'], self.movies_single_connector))

    def go_back_to_movies(self, *args):
        if 'latest view main screen' in self.manager.screen_names:
            Logger.info('back from latest')

            self.manager.current = 'latest view main screen'

        elif 'search view main screen' in self.manager.screen_names:
            Logger.info('back from search')

            self.manager.current = 'search view main screen'

        elif 'favourites view main screen' in self.manager.screen_names:
            Logger.info('back from favourites')

            self.manager.current = 'favourites view main screen'

        else:
            Logger.info('back from movies')

            self.manager.current = 'movies view main screen'

        self.manager.remove_widget(self.movies_main_single_screen_instance)


class MoviesViewMain(Screen):

    def __init__(self, parent_instance, **kwargs):
        super(MoviesViewMain, self).__init__(**kwargs)
        self.name = 'movies view main screen'
        Logger.info('MoviesViewMain: Initialized {}'.format(self.name))

        self.animation = c_i.ItemAnimation()
        movies_layout, movies_grid = util_f.create_scroll_view(c_i.UNIQUE_V_W, c_i.SHO_V_H,
                                                               on_scroll_a=self.sch_ref)

        self.ids.movies_view_main_container.add_widget(movies_layout)

        self.refreshed = None
        self.parent_instance = parent_instance
        hashed_dic_movies = ViewControl.d_data['hashed_dic_movies']['val']

        try:
            util_f.add_item_w(self, hashed_dic_movies, Item, MainView, movies_grid, util_f.change_to_movies_single,
                              type='movie', counter_limit=50)
            Logger.info('MoviesViewMain: Finished adding items for  movies')
        except Exception as e:
            Logger.warning('MoviesViewMain: Adding movies failed due to {}'.format(e))
            pass


    def sch_ref(self, *args):
        scroller = args[0].scroll_y
        if not self.refreshed:
            if scroller < -0.05:
                Clock.schedule_once(self.do_refresh, 1.2)
                self.refreshed = True
        else:
            Logger.info('MoviesViewMain: refresh done')

    def do_refresh(instance, *args):
        instance.parent_instance.m_paginator_buton_call(instance.parent_instance.current_pag)


class ScMaMovies(ScreenManager):

    def __init__(self, movies_view_instance, **kwargs):
        super(ScMaMovies, self).__init__(**kwargs)
        Logger.info('ScMaMovies: Initialized {}'.format(self))

        self.movies_view_inst = movies_view_instance

        # util_f.add_widget_with_loading(App.get_running_app().loader_overlay, c_i.w_l_start, c_i.w_l_stop, self.add_scmm)

    def add_scmm(self, *args):
        self.add_widget(MoviesViewMain(self.movies_view_inst))


class PaginationButton(ToggleButton):

    def __init__(self, set_as_text, _type, holder, sc_inst, _par_inst, media_db, filter_db, **kwargs):
        super(PaginationButton, self).__init__(**kwargs)
        self.text = set_as_text
        self._type = _type
        self.holder = holder
        self.filt = filter_db
        self._db_d = media_db
        self.group = _type
        self._par_inst = _par_inst
        self.screen_manager_inst = sc_inst

    def _paginator_buton_call_wrap(self, *args):
        if self.state == 'down':
            self.color = YELLOW
        else:
            self.color = WHITE
        util_f._paginator_buton_call(self)


class MoviesView(Screen):
    skipper = BooleanProperty(True)

    def __init__(self, **kwargs):
        super(MoviesView, self).__init__(**kwargs)
        Logger.info('MoviesView: Initialized {}'.format(self))

        self.media = App.get_running_app().media
        self.filter = App.get_running_app().filter


        try:
            movies_layout, movies_grid = util_f.create_scroll_view_horizontal()

            for i in range(1, 50):
                self.btn_s_p = PaginationButton(str(i), 'm', self.ids.mov_view_holder, ScMaMovies, self, self.media, self.filter)
                movies_grid.add_widget(self.btn_s_p)
        except Exception as e:
            Logger.info('fail m {}'.format(e))

            # self.btn_m_p = PaginationButton(str(i))
            # self.btn_m_p.bind(on_press=lambda instance: self.m_paginator_buton_call(instance))
            # self.movies_paginator.add_widget(self.btn_m_p)

        movies_layout.add_widget(movies_grid)
        self.ids.movies_pag_holder.add_widget(movies_layout)

        # self.current_pag = self.movies_paginator.children[len(self.movies_paginator.children)-1]
        # self.current_pag.background_color = get_color_from_hex('#ffa500')
        #
        # self.scroll = ScrollView(size_hint=(1, 1), do_scroll_x=True, do_scroll_y=False, bar_color=[0,0,0,0], bar_inactive_color=[0,0,0,0])
        #
        # self.scroll.add_widget(self.movies_paginator)
        # self.ids.movies_pag_holder.add_widget(self.scroll)
        self.ids.mov_view_holder.add_widget(ScMaMovies(self))

    # def _add_movies(self, *args):
    #     self.ids.mov_view_holder.clear_widgets()
        # self.ids.mov_view_holder.add_widget(ScMaMovies(self))

    # def m_paginator_buton_call(self, paginator_button_instance, *args):
    #
    #     for pag_bu in self.movies_paginator.children:
    #         pag_bu.background_color = [1, 1, 1, 1]
    #
    #     self.ids.mov_view_holder.remove_widget(self.ids.mov_view_holder.children[0])
    #
    #
    #     paginator_button_instance.background_color = get_color_from_hex('#ffa500')
    #
    #     x_sort = ViewControl.f_data['sort']['val']
    #     x_order = ViewControl.f_data['order']['val']
    #     x_genre = ViewControl.f_data['genre']['val']
    #     if not x_order or x_order is None:
    #         Logger.info('MoviesView: _filter_order setting to default cause is  {}'.format(x_order))
    #
    #         x_order = '-1'
    #     if not x_sort or x_sort is None:
    #         Logger.info('MoviesView: _filter_sort setting to default cause is  {}'.format(x_sort))
    #
    #         x_sort = 'last added'
    #
    #
    #     _get_api(self, Movies(page=paginator_button_instance.text, order=x_order, sort=x_sort, genre=x_genre).get_search())
    #
    #     self.ids.mov_view_holder.add_widget(ScMaMovies(self))
    #
    #     self.current_pag = paginator_button_instance


class Item(BoxLayout):

    def __init__(self, _imdb_id, favo, **kwargs):
        super(Item, self).__init__(**kwargs)
        Logger.info('Item: Initialized {}'.format(self))

        self.megs = _imdb_id
        self._favourite = favo
        Logger.info('Item: _imdb_id {}'.format(self.megs))
        Logger.info('Item: favourite {}'.format(self._favourite))


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


class ShowEpSyn(BoxLayout):

    def __init__(self, _show_episode_synopsis_text_in, **kwargs):
        super(ShowEpSyn, self).__init__(**kwargs)
        Logger.info('SeriesViewMainSingle: ShowEpSyn Initialized {}'.format(self))

        self._show_episode_synopsis_text_in = _show_episode_synopsis_text_in
        self.ids.show_episode_syn.text = self._show_episode_synopsis_text_in


class SeriesViewMainSingle(Screen):

    def __init__(self, series_id, **kwargs):
        super(SeriesViewMainSingle, self).__init__(**kwargs)
        self.series_single_connector = c_i.Connector()

        self.series_id = series_id
        print(self.series_id)
        self.name = 'svms'
        self.series_main_singe_screen_instance = self
        self.media = App.get_running_app().media

        Logger.info('SeriesViewMainSingle: Initialized {}'.format(self.name))

        self.buffe = []
        hashed_dic_show = self.media._get('hashed_dic_show')
        # print(hashed_dic_show)
        # for i in hashed_dic_show:
        #     print(i)
        hash_map = self.media._get(key='hashed_dic_show', child_key='val')[hash_item_m(self.series_id)]
        print(hash_map)

        # for _single_show_item_in_dic in hashed_dic_show:
        #     for show_node in hashed_dic_show[_single_show_item_in_dic]:
        #         print('.................................................')
        #         print('show node {}'.format(show_node))
        #         print('single show item in dic {}'.format(_single_show_item_in_dic))
        #         print('hashed_dic_show[_single_show_item_in_dic] {} '.format(hashed_dic_show[_single_show_item_in_dic]))
        #
        #         if show_node == 'episodes':
        #             self.episode_count = int(len(hashed_dic_show[_single_show_item_in_dic]['episodes']))
        #             self.accord_height = dp((1 * 44) + 340)
        #
        #             self._single_show_accordion = Accordion(orientation='vertical', height=self.accord_height, size_hint_y=None, min_space=dp(44))
        #
        #             self._single_show_accordion.id = 'testAccordian'
        #
        #             self.g_scroll_list = ScrollView(size_hint=(None, None),
        #                                             size=(c_i.width_x - 40, c_i.height_x * 0.4), on_scroll_move=self.sch_lazy, pos_hint={'center_x': 0.5, 'center_y': 0.5})
        #
        #             self.ids.series_view_main_single_container_se.add_widget(self.g_scroll_list)
        #             self.g_scroll_list.add_widget(self._single_show_accordion)
        #
        #             Logger.info('SeriesViewMainSingle: Show level >>>>>')
        #
        #             Logger.info('SeriesViewMainSingle: Show title {}'.format(hashed_dic_show[_single_show_item_in_dic]['title']))
        #             _show_t = str(hashed_dic_show[_single_show_item_in_dic]['title']).encode('utf-8')
        #             self.ids.series_view_main_single_nav_title_t.text = str(_show_t)
        #
        #             Logger.info('SeriesViewMainSingle: Show year {}'.format(hashed_dic_show[_single_show_item_in_dic]['year']))
        #             _show_y = str(hashed_dic_show[_single_show_item_in_dic]['year'])
        #             _show_y = _show_y.encode('utf-8')
        #
        #             # Logger.info(' Show synopsis {}'.format(hashed_dic_show[_single_show_item_in_dic]['synopsis']))
        #             _show_s = hashed_dic_show[_single_show_item_in_dic]['synopsis']
        #             _show_s = _show_s.encode('utf-8')
        #
        #             Logger.info('SeriesViewMainSingle: Show runtime {}'.format(hashed_dic_show[_single_show_item_in_dic]['runtime']))
        #             _show_r = str(hashed_dic_show[_single_show_item_in_dic]['runtime'])
        #             _show_r = _show_r.encode('utf-8')
        #
        #             try:
        #                 Logger.info('SeriesViewMainSingle: Show image {}'.format(hashed_dic_show[_single_show_item_in_dic]['images']['poster'].replace('https', 'http')))
        #                 _show_im = str(hashed_dic_show[_single_show_item_in_dic]['images']['poster'])
        #                 _show_im = _show_im.replace('https', 'http')
        #             except KeyError:
        #                 Logger.warning('SeriesViewMainSingle: Show image fallback{}')
        #                 _show_im = './images/logo.png'
        #                 pass
        #
        #             Logger.info('SeriesViewMainSingle: Show status {}'.format(hashed_dic_show[_single_show_item_in_dic]['status']))
        #             _show_st = str(hashed_dic_show[_single_show_item_in_dic]['status'])
        #             _show_st = _show_st.encode('utf-8')
        #
        #             Logger.info('SeriesViewMainSingle: Show number of episodes {}'.format(len(hashed_dic_show[_single_show_item_in_dic]['episodes'])))
        #             self._ep_num = len(hashed_dic_show[_single_show_item_in_dic]['episodes'])
        #
        #             self.ids.series_view_main_single_container.add_widget(
        #                 SeriesViewMainSingleTop(_show_y, _show_s, _show_r, _show_im, _show_st))
        #             lok = 0
        #             for _episode_node in hashed_dic_show[_single_show_item_in_dic][show_node]:
        #                 lok += 1
        #                 acc_item = AccordionItem(collapse=True, orientation='vertical', background_normal='./images/ti.png', background_selected='./images/ti.png')
        #
        #                 acc_item.container.orientation = 'vertical'
        #                 Logger.info('SeriesViewMainSingle: Episode level >>>>>')
        #                 # Logger.info(z)
        #                 try:
        #                     Logger.info('SeriesViewMainSingle: Episode title {}'.format(_episode_node['title']))
        #                 except UnicodeEncodeError:
        #                     pass
        #
        #                 if _episode_node['title']:
        #                     ti = _episode_node['title'].encode('utf-8')
        #                     if len(ti) > 42:
        #                         ti = '{}...'.format(ti[:41])
        #                 else:
        #                     ti = ''
        #
        #                 Logger.info('SeriesViewMainSingle: Episode overview')
        #                 if _episode_node['overview']:
        #                     _show_episode_over = _episode_node['overview']
        #                     _show_episode_over = _show_episode_over.encode('utf-8')
        #                     Logger.info('SeriesViewMainSingle: Episode overview {}'.format(_show_episode_over))
        #                 else:
        #                     _show_episode_over = ''
        #
        #                 Logger.info('SeriesViewMainSingle: Episode episode number {}'.format(_episode_node['episode']))
        #                 _show_episode = str(_episode_node['episode'])
        #                 _show_episode = _show_episode.encode('utf-8')
        #
        #                 Logger.info('SeriesViewMainSingle: Episode season number {}'.format(_episode_node['season']))
        #                 _show_season = str(_episode_node['season'])
        #                 _show_season = _show_season.encode('utf-8')
        #
        #                 acc_item.title = '{} {} {}'.format(ti, _show_season, _show_episode)
        #
        #                 _show_accordion_item_container_synopsis = ShowEpSyn(str(_show_episode_over))
        #
        #                 acc_item.container.add_widget(_show_accordion_item_container_synopsis)
        #
        #                 acc_item.container.add_widget(Tor(_episode_node['torrents'], self.series_single_connector))
        #
        #                 self.buffe.append(acc_item)
        #
        #                 if lok < 5:
        #                     self.lazyy()

    def sch_lazy(self, *args):

        scroller = args[0].scroll_y
        if scroller < -0.1:
            Clock.schedule_once(self.lazyy, 1.2)

    def lazyy(instance, *args):
        if instance.buffe:
            instance._single_show_accordion.height += dp(44)
            item_from_buff = instance.buffe[0]

            instance._single_show_accordion.add_widget(item_from_buff)
            instance.buffe.remove(item_from_buff)

    def go_back_to_series(self, *args):

        if 'latest view main screen' in self.manager.screen_names:
            Logger.info('back from latest')
            self.manager.current = 'latest view main screen'

        elif 'search view main screen' in self.manager.screen_names:
            Logger.info('back from search')
            self.manager.current = 'search view main screen'

        elif 'favourites view main screen' in self.manager.screen_names:
            Logger.info('back from favourites')
            self.manager.current = 'favourites view main screen'

        else:
            Logger.info('back from series')
            self.manager.current = 'series view main screen'

        self.manager.remove_widget(self.series_main_singe_screen_instance)


class SeriesViewMain(Screen):

    def __init__(self, parent_hold=None, **kwargs):
        super(SeriesViewMain, self).__init__(**kwargs)
        self.name = 'series view main screen'
        Logger.info('SeriesViewMain: Initialized {}'.format(self.name))

        self.animation = c_i.ItemAnimation()
        self.favourites = App.get_running_app().favourites
        self.media = App.get_running_app().media

        self.parent_hold = parent_hold
        self.instance_to_add = ScMaFavourites

        self.series_layout, self.series_grid = util_f.create_scroll_view(c_i.UNIQUE_V_W, c_i.SHO_V_H, on_scroll_a=util_f.sch_ref, on_scroll_ar=self)
        self.ids.series_view_main_container.add_widget(self.series_layout)

        self.hashed_dic_shows = self.media._get('hashed_dic_shows')

        self.refreshed = None

        try:
            Logger.info('SeriesViewMain: started adding items for series')

            util_f.add_item_w(self, self.hashed_dic_shows, Item, self.series_grid,
                              util_f.change_to_series_single, type='show', counter_limit=50,
                              _widget_=SeriesViewMainSingle, _media_db=self.media, _favourites_db=self.favourites)
            Logger.info('SeriesViewMain: Finished adding items for  shows')
        except Exception as e:
            Logger.warning('SeriesViewMain: Adding shows failed due to {}'.format(e))
            pass


class ScMaSeries(ScreenManager):
    def __init__(self, parent_hold=None, **kwargs):
        super(ScMaSeries, self).__init__(**kwargs)
        Logger.info('ScMaSeries: Initialized {}'.format(self))

        Cache.append('screen_cache', 'series', self)
        self.parent_hold = parent_hold

        util_f.add_widget_with_loading(self.add_scms)

    @util_f.schedule_once_no_args(timing=1)
    def add_scms(self, *args):
        self.add_widget(SeriesViewMain(self.parent_hold))


class SeriesView(Screen):

    def __init__(self, **kwargs):
        super(SeriesView, self).__init__(**kwargs)
        Logger.info('SeriesView: Initialized {}'.format(self))

        self.media = App.get_running_app().media
        self.filter = App.get_running_app().filter

        try:
            self.series_layout, self.series_grid = util_f.create_scroll_view_horizontal()

            for i in range(1, 50):
                self.btn_s_p = PaginationButton(str(i), 's', self.ids.ser_view_holder, ScMaSeries, self, self.media, self.filter)

                self.series_grid.add_widget(self.btn_s_p)
        except Exception as e:
            Logger.info('SeriesView: Adding pagination buttons failed due to {}'.format(e))

        self.series_layout.add_widget(self.series_grid)

        self.ids.series_pag_holder.add_widget(self.series_layout)

    def load_on_enter(self, *args):
        util_f.resolve_enter_screen(self, 'series', self.ids.ser_view_holder, ScMaSeries)


class SearchViewMain(Screen):

    def __init__(self, search_type, **kwargs):
        super(SearchViewMain, self).__init__(**kwargs)
        self.name = 'search view main screen'
        Logger.info('SearchViewMain: Initialized {}'.format(self.name))

        self.typ = search_type
        self.ids.search_typee.text = self.typ
        self.media = App.get_running_app().media
        self.favourites = App.get_running_app().favourites
        self.animation = c_i.ItemAnimation()

        hashed_dic_search = self.media._get(key='hashed_dic_search')

        # SHOWS SEARCH
        if self.typ == 'Shows':

            search_series_layout, search_series_grid = util_f.create_scroll_view(c_i.UNIQUE_V_W, c_i.SHO_V_H)
            self.ids.search_view_main_container_holder.add_widget(search_series_layout)

            try:
                util_f.add_item_w(self, hashed_dic_search, Item, search_series_grid,
                                  util_f.change_to_series_single, type='show', counter_limit=50,
                                  _widget_=SeriesViewMainSingle, _media_db=self.media, _favourites_db=self.favourites)
                Logger.info('SearchViewMain: Finished adding items for search shows')
            except Exception as e:
                Logger.warning('SearchViewMain: search shows failed due to {}'.format(e))
                pass

        # MOVIES SEARCH
        else:
            search_movies_layout, search_movies_grid = util_f.create_scroll_view(c_i.UNIQUE_V_W, c_i.SHO_V_H)
            self.ids.search_view_main_container_holder.add_widget(search_movies_layout)

            try:
                util_f.add_item_w(self, hashed_dic_search, Item, search_movies_grid,
                                  util_f.change_to_movies_single, type='movie', counter_limit=50,
                                  _widget_=MoviesViewMainSingle, _media_db=self.media, _favourites_db=self.favourites)
                Logger.info('SearchViewMain: Finished adding items for latest movies')
            except Exception as e:
                Logger.warning('SearchViewMain: search movies failed due to {}'.format(e))
                pass


class ScMaSearch(ScreenManager):

    def __init__(self, search_type, **kwargs):
        super(ScMaSearch, self).__init__(**kwargs)
        Logger.info('ScMaSearch: Initialized {}'.format(self))

        self.search_type = search_type

        if SearchView.skipper:
            self.add_scmsr()
        else:
            util_f.add_widget_with_loading(self.add_scmsr)

    @util_f.schedule_once_no_args(timing=1)
    def add_scmsr(self, *args):
        self.add_widget(SearchViewMain(self.search_type))
        SeriesView.skipper = False


class SearchView(Screen):

    skipper = BooleanProperty(True)

    def __init__(self, _search_keywords=None, **kwargs):
        super(SearchView, self).__init__(**kwargs)
        Logger.info('SearchView: Initialized {}'.format(self))

        self.filter = App.get_running_app().filter
        self.media = App.get_running_app().media
        self._search_keywords = _search_keywords
        util_f.clear_widgets(self.ids.search_view_holder)

    def on_search_screen_enter(self, *args):
        typ = self.filter._get(key='type')

        if typ and typ == 'Shows':
            self.get_media_content(Shows(page='1', order=self.filter._get(key='order'), sort=self.filter._get(key='sort'),
                  genre=self.filter._get(key='genre'), keywords=self._search_keywords).get_search(), 1)
            Logger.info('SearchView: on_search_screen_enter for {}'.format(typ))
        else:
            typ = 'Movies'
            self.get_media_content(
                Movies(page='1', order=self.filter._get(key='order'), sort=self.filter._get(key='sort'),
                       genre=self.filter._get(key='genre'), keywords=self._search_keywords).get_search(), 1)
            Logger.info('SearchView: on_search_screen_enter for {}'.format(typ))

        self.ids.search_view_holder.add_widget(ScMaSearch(typ))

    @util_f.schedule_once_two_arg_timing(timing=None)
    def get_media_content(self, api_instance, *args):
        Logger.info('SearchView: get_media_content invoked')

        """get search movies and series, populate shows dictionary populate movies dicionary"""

        util_f._get_api(self, api_instance, self.media)


class LatestViewMain(Screen):

    def __init__(self, **kwargs):
        super(LatestViewMain, self).__init__(**kwargs)
        self.name = 'latest view main screen'
        Logger.info('LatestViewMain: Initialized {}'.format(self.name))

        self.animation = c_i.ItemAnimation()
        self.media = App.get_running_app().media
        self.favourites = App.get_running_app().favourites

        hashed_dic_shows = self.media._get(key='hashed_dic_shows')
        hashed_dic_movies = self.media._get(key='hashed_dic_movies')

        # SHOWS LATEST
        latest_series_layout, latest_series_grid = util_f.create_scroll_view(c_i.UNIQUE_V_W, c_i.LAT_V_H)
        self.ids.latest_view_main_shows_container.add_widget(latest_series_layout)

        try:
            util_f.add_item_w(self, hashed_dic_shows, Item, latest_series_grid,
                              util_f.change_to_series_single, type='show', counter_limit=15, _widget_=SeriesViewMainSingle, _media_db=self.media, _favourites_db=self.favourites)
            Logger.info('Finished adding items for latest shows')
        except Exception as e:
            Logger.warning('LatestViewMain: latest shows failed due to {}'.format(e))
            pass

        # MOVIES LATEST
        latest_movies_layout, latest_movies_grid = util_f.create_scroll_view(c_i.UNIQUE_V_W, c_i.LAT_V_H)
        self.ids.latest_view_main_movies_container.add_widget(latest_movies_layout)

        try:
            util_f.add_item_w(self, hashed_dic_movies, Item, latest_movies_grid,
                              util_f.change_to_movies_single, type='movie', counter_limit=15, _widget_=MoviesViewMainSingle,  _media_db=self.media, _favourites_db=self.favourites)
            Logger.info('Finished adding items for latest movies')
        except Exception as e:
            Logger.warning('LatestViewMain: latest movies failed due to {}'.format(e))
            pass


class ScMaLatest(ScreenManager):

    def __init__(self, **kwargs):
        super(ScMaLatest, self).__init__(**kwargs)
        Logger.info('ScMaLatest: Initialized {}'.format(self))

        if LatestView.skipper:
            self.add_scms()
        else:
            util_f.add_widget_with_loading(self.add_scms)

    @util_f.schedule_once_no_args(timing=1)
    def add_scms(self, *args):
        self.add_widget(LatestViewMain())


class LatestView(Screen):

    skipper = BooleanProperty(True)

    def __init__(self, **kwargs):
        super(LatestView, self).__init__(**kwargs)
        Logger.info('LatestView: Initialized {}'.format(self))

        self.media = App.get_running_app().media
        self.filter = App.get_running_app().filter

        self.ids.lat_view_holder.add_widget(ScMaLatest())

    # def refresh_on_scroll(self, *args):
    #     Logger.info('LatestView: refresh invoked {} {}'.format(self, LatestView.skipper))
    #
    #     if not LatestView.skipper:
    #         self.ids.lat_view_holder.remove_widget(self.ids.lat_view_holder.children[0])
    #         Logger.info('LatestView: refresh not skipped {}'.format(self))
    #
    #         self.get_media_content(Movies(order='-1', sort='last added', genre=self.filter._get(key='genre')).get_search(), 2)
    #         self.get_media_content(Shows(order='-1', sort='updated', genre=self.filter._get(key='genre')).get_search(), 4)
    #
    #         self.ids.lat_view_holder.add_widget(ScMaLatest())
    #
    #     else:
    #         Logger.info('LatestView: refresh skipped {}'.format(self))
    #         LatestView.skipper = False

    # @util_f.schedule_once_two_arg_timing(timing=None)
    # def get_media_content(self, api_instance, *args):
    #     Logger.info('LatestView: get_media_content invoked')
    #
    #     """get inital latest movies and series, populate shows dictionary populate movies dicionary"""
    #
    #     util_f._get_api(self, api_instance, self.media)


class FavouritesViewMain(Screen):

    def __init__(self, parent_hold=None, **kwargs):
        super(FavouritesViewMain, self).__init__(**kwargs)
        self.name = 'favourites view main screen'
        Logger.info('FavouritesViewMain: Initialized {}'.format(self.name))

        self.favourites = App.get_running_app().favourites
        self.media = App.get_running_app().media
        self.animation = c_i.ItemAnimation()

        self.parent_hold = parent_hold
        self.instance_to_add = ScMaFavourites

        self.favourites_layout, self.favourites_grid = util_f.create_scroll_view(c_i.UNIQUE_V_W, c_i.FAV_V_H, on_scroll_a=util_f.sch_ref, on_scroll_ar=self)
        self.ids.favourites_view_main_container_holder.add_widget(self.favourites_layout)

        self.hashed_favourites = self.favourites._get_keys()

        self.refreshed = None

        try:
            Logger.info('FavouritesViewMain: started adding items for favourites')

            util_f.add_item_w(self, self.hashed_favourites, Item, self.favourites_grid, util_f.change_to_movies_single, favourites=True, addi_ch=util_f.change_to_series_single, counter_limit=30, _media_db=self.media, _favourites_db=self.favourites)
            Logger.info('FavouritesViewMain: Finished adding items for favourites')
        except Exception as e:
            Logger.warning('FavouritesViewMain: favourites failed due to {}'.format(e))
            pass


class ScMaFavourites(ScreenManager):

    def __init__(self, parent_hold=None, **kwargs):
        super(ScMaFavourites, self).__init__(**kwargs)
        Logger.info('ScMaFavourites: Initialized {}'.format(self))

        Cache.append('screen_cache', 'favourites', self)
        self.parent_hold = parent_hold

        util_f.add_widget_with_loading(self.add_scmf)

    @util_f.schedule_once_no_args(timing=1)
    def add_scmf(self, *args):
        self.add_widget(FavouritesViewMain(parent_hold=self.parent_hold))


class FavouritesView(Screen):

    def __init__(self, **kwargs):
        super(FavouritesView, self).__init__(**kwargs)
        Logger.info('FavouritesView: Initialized {}'.format(self))

    def load_on_enter(self, *args):
        util_f.resolve_enter_screen(self, 'favourites', self.ids.fav_view_holder, ScMaFavourites)


class MainViewScManager(ScreenManager):

    def __init__(self, **kwargs):
        super(MainViewScManager, self).__init__(**kwargs)
        Logger.info('MainViewScManager: Initialized {}'.format(self))

        sc_list = [LatestView, MoviesView, SeriesView, FavouritesView]
        self.plex_instance = App.get_running_app().plex_inst
        schedule_count = 0

        for screen in sc_list:

            self.screen_add(screen(), schedule_count)
            schedule_count += 1
        try:
            self.plex_instance._get_token()
        except KeyError as e:
            Logger.warning('MainViewScManager: no server set for plex {}'.format(e))
            pass

    @util_f.schedule_once_two_arg_timing(timing=2)
    def screen_add(self, screen, timings, *args):
        self.add_widget(screen)


class FilterModalView(ModalView):

    def __init__(self, **kwargs):
        super(FilterModalView, self).__init__(**kwargs)
        Logger.info('FilterModalView: Initialized {}'.format(self))

        self.size = (Window.size[0] / 1.5, Window.size[1] / 1.5)
        self.ids.filter_genre.dropdown_cls.max_height = dp(350)
        self.filter = App.get_running_app().filter

    def close_filter(self, filter_type, filter_genre, filter_order, filter_sort, *args):
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

        self.filter._put(key='order', val=self.filter_order)
        self.filter._put(key='genre', val=self.filter_genre)
        self.filter._put(key='type', val=self.filter_type)
        self.filter._put(key='sort', val=self.filter_sort)

    def hide_other_accordions(instances, _filter_dropdown_focused):
        for spinner_child in instances.ids.filter_view_container.children[0].children:
            spinner_child.opacity = 0.2
        _filter_dropdown_focused.opacity = 1


class MainNavButton(ToggleButton):

    def __init__(self, set_as_text, **kwargs):
        super(MainNavButton, self).__init__(**kwargs)
        self.text = set_as_text

    def stater(self, *args):
        if self.state == 'down':
            self.color = YELLOW
        else:
            self.color = WHITE


class SlideMenuScrollUpper(BoxLayout):
    def __init__(self, main_instance, **kwargs):
        super(SlideMenuScrollUpper, self).__init__(**kwargs)
        Logger.info('SlideMenuScrollUpper: Initialized {}'.format(self))
        self.parent_inst = main_instance

    def _sign_in_out(self, *args):
        self.parent_inst.sign_in_out()


class SlideMenu(BoxLayout):
    def __init__(self, main_instance, **kwargs):
        super(SlideMenu, self).__init__(**kwargs)
        Logger.info('SlideMenu: Initialized {}'.format(self))
        self.width = Window.size[0]
        self.height = Window.size[1]
        self.plex_instance = App.get_running_app().plex_inst
        self.parent_instance = main_instance

        slide_scroll_content_layout = GridLayout(cols=1, padding=25, spacing=15,
                                       size_hint=(None, None), width=c_i.width_x - 30)
        slide_scroll_content_layout.bind(minimum_height=slide_scroll_content_layout.setter('height'))

        slide_scroll_content_layout_scroll_list = ScrollView(size_hint=(None, None),
                                            size=(self.width - 20, self.height * 0.94), pos_hint={'center_x': 0.5, 'center_y': .5}, do_scroll_x=False)

        slide_scroll_content_layout_scroll_list.add_widget(slide_scroll_content_layout)
        self.ids.bobi.add_widget(slide_scroll_content_layout_scroll_list)

        ssclayout = GridLayout(cols=1, rows=2, padding=25, spacing=15,
                                                 size_hint=(None, None), width=self.width - 30)
        self.pi = SlideMenuScrollUpper(self)
        ssclayout.add_widget(self.pi)
        for i in range(5):
            self.pi.ids.upper_grid.add_widget(Label(text=str(i)))

        self.set_account_options()

        slide_scroll_content_layout.add_widget(ssclayout)

        # slide_scroll_content_layout.add_widget(Label(text='kurac', size_hint=(None, None), width=500, height=600))

        for i in range(25):

            slide_scroll_content_layout.add_widget(Button(text=str(i),size_hint=(None, None),width=500,height=250))

    def close_slide_menu(self, *args):

        animate = Animation(pos_hint={'center_x': -.5, 'center_y': .5}, duration=0.7)
        animate.start(self)

    def set_account_options(self, *args):
        if self.plex_instance.check_stored_credentials():
            self.pi.ids.account_name_l.text = self.plex_instance.get_stored_credentials()[0]
            self.pi.ids.account_butt.text = 'Sign Out'
        else:
            Logger.info('no account')
            self.pi.ids.account_butt.text = 'Sign In'

    def sign_in_out(self, *args):
        self.plex_instance.remove_plex_config()
        if 'LoginScreen' not in self.parent_instance.manager.screen_names:
            Logger.info('SlideMenu: sign_in_out > creating login view')

            util_f.scm_switch_to_transition(self.parent_instance, LoginView())
        else:
            Logger.info('SlideMenu: sign_in_out > login view exists')

            self.parent_instance.manager.current = 'LoginScreen'


class MainView(Screen):

    connection_status_indicator = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(MainView, self).__init__(**kwargs)
        Logger.info('MainView: Initialized {}'.format(self))

        self.view = App.get_running_app().filter_modal
        self.main_scm = MainViewScManager()
        self.slide_menu = SlideMenu(self)

        self.scroll, self.main_nav_p = util_f.create_scroll_view_horizontal(columns=4)

        util_f._add_navigation_buttons(self, MainNavButton)

        self.scroll.add_widget(self.main_nav_p)
        self.ids.navigation_b.add_widget(self.scroll)

        self.ids.screen_m_container.add_widget(self.main_scm)

        self.add_widget(self.slide_menu)

    def open_slide_menu(self, *args):

        animate = Animation(pos_hint={'center_x': .5, 'center_y': .5}, duration=c_i.sm_anim_time)
        animate.start(self.slide_menu)

    @util_f.schedule_once_no_args(timing=4)
    def connect_on_enter(self, *args):
        Logger.info('MainView: on enter create connector')

        self.connector = c_i.Connector()

        Logger.info('MainView: connection state {}'.format(self.connector.server_state))

        self.update_status_in(self.connector.server_state)

        Logger.info('MainView: update connection indicator to {}'.format(self.connector.server_state))

    def open_filter_view(self, *args):
        Logger.info('MainView: open_filter_view invoked')

        self.view.open()

    def set_as_current_screen(self, scn, *args):
        Logger.info('MainView: setting active screen {}'.format(scn))

        self.main_scm.current = scn

    def set_as_current_screen_search(self, _search_keywords, *args):
        Logger.info('MainView: setting active screen for search ')

        if self.main_scm.has_screen('search_view'):
            self.main_scm.current = 'search_view'
        else:
            self.main_scm.add_widget(SearchView(_search_keywords))
            self.main_scm.current = 'search_view'

    def searchInput_on_focus_effect(self, _search_input_box, _search_input_focus, *args):
        if _search_input_focus:
            self.ids.search_input.width = dp(200)
            _search_input_box.hint_text = ''
            _search_input_box.opacity = 1

        else:
            _search_input_box.opacity = .2
            self.ids.search_input.width = dp(100)

    def _search(self, _search_keywords, *args):
        Logger.info('MainView: _search invoked with {}'.format(_search_keywords))

        if _search_keywords:
            self.set_as_current_screen_search(_search_keywords)
        else:
            Logger.error('MainView: _search invoked without params. Skipping')

    def update_status_in(self, status_flagger_flag, *args):
        Logger.info('MainView: Updating connection status invoked')
        # self.slide_menu.pi.ids.kkl.color = get_color_from_hex('#7B6FE7')

        # if status_flagger_flag:
            # self.ids.connection_status_ind_l.source = 'images/on_connection.png'
            # self.slide_menu.ids.connection_status_ind_ll.source = 'images/on_connection.png'


        # else:
            # self.ids.connection_status_ind_l.source = 'images/no_connection.png'
            # self.slide_menu.ids.connection_status_ind_ll.source = 'images/no_connection.png'


class ScanViewItem(BoxLayout):

    def __init__(self, device_name_for_label, online=False, **kwargs):
        super(ScanViewItem, self).__init__(**kwargs)
        Logger.info('ScanViewItem: Initialized {}'.format(self))

        self.ids.scan_i_label.text = device_name_for_label
        if online:
            self.ids.scan_i_label.color = get_color_from_hex('#FFBA1B')

    def scan_i_pressed(self, instance, *args):
        args[0]._do_press()
        if args[0].active:
            self.redraw_canvas(instance, 'images/list_it_d.png')

            ScanView.choosen_device = self.ids.scan_i_label.text

    def scan_i_checked(self, instance, *args):
        if args[0].state == 'normal':
            self.redraw_canvas(instance, 'images/list_it.png')

    def redraw_canvas(self, instance, image):
        instance.canvas.before.clear()
        instance.size_hint = (None, None)
        instance.width = dp(300)
        instance.height = dp(120)
        instance.pos_hint = {'center_x': .5, 'center_y': .5}

        with instance.canvas.before:
            Rectangle(source=image, pos=instance.pos, size=instance.size)


class ScanView(Screen):

    choosen_device = StringProperty()

    def __init__(self, plex_server=None, **kwargs):
        super(ScanView, self).__init__(**kwargs)
        Logger.info('ScanView: Initialized {} with args {}'.format(self, str(plex_server)))

        self.plex_inst = App.get_running_app().plex_inst
        self._plex_server_dict = plex_server
        self.connector = App.get_running_app().connection_inst
        self.network_inst = App.get_running_app().network_inst

        if self._plex_server_dict:
            for i in self._plex_server_dict:
                self.add_scan_view_item(i)

    def scan_available_network(self, _subnet_in, *args):

        scan_network_for_single_connection(_subnet_in, self.network_inst)

    def set_as_host(self, host_in):
        Logger.info('ScanView: set_as_host {}'.format(host_in))

        breaker = host_in.find('/')
        prepare_url = host_in[breaker+1:]
        self.plex_inst.store_server(host_in[:breaker], prepare_url)
        self.connector.url = prepare_url

        Logger.info('ScanView: set_as_host Connector.url  {}'.format(self.connector.url))

    def save_and_go_to_main(self, *args):
        Logger.info('ScanView: Save and go to main screen')

        if self.choosen_device:
            self.set_as_host(self.choosen_device)
            Logger.info('ScanView: setting up device for connection {}'.format(self.choosen_device))

        Logger.info('ScanView: switching to MainView')
        util_f.scm_switch_to_transition(self, MainView())
        util_f.busy_loading_overlay(0, 8)

    @util_f.schedule_once_one_arg(-1)
    def add_scan_view_item(self, iter_item, *args):

        online = False
        Logger.info('ScanView: add_scan_view_item for {}'.format(iter_item))

        self.scan_available_network(self._plex_server_dict[iter_item])
        self.formated_serv_name = '{}/{}'.format(iter_item, self._plex_server_dict[iter_item])

        self._urls_list = self.network_inst._get_keys()
        Logger.info('ScanView: urls scanned online {}'.format(self._urls_list))

        if self._plex_server_dict[iter_item] in self._urls_list:

            online = True

        self.ids.plex_server_list_grid.add_widget(ScanViewItem(self.formated_serv_name, online=online))
        Logger.info('ScanView: adding {} online {}'.format(self.formated_serv_name, online))


# class SettingsViewItem(BoxLayout):
#
#     def __init__(self, device_name_for_label, **kwargs):
#         super(SettingsViewItem, self).__init__(**kwargs)
#         Logger.info('SettingsViewItem: Initialized {}'.format(self))
#
#         self.dev_name_for_l = device_name_for_label
#         self.ids.settings_view_i_name.text = self.dev_name_for_l
#
#     def return_on_active_name(self, settings_item_checkbox_flag, settings_item_checkbox_value, *args):
#         Logger.info('SettingsViewItem: return_on_active_name invoked')
#
#         if settings_item_checkbox_flag:
#             SettingsView.choosen_device = settings_item_checkbox_value
#         else:
#             SettingsView.choosen_device = ''
#
#
# class SettingsView(Screen):
#     choosen_device = StringProperty()
#
#     def __init__(self, **kwargs):
#         super(SettingsView, self).__init__(**kwargs)
#         Logger.info('SettingsView: Initialized {}'.format(self))
#
#         self.update_list_devices()
#
#     def scan_again(self, *args):
#         Logger.info('SettingsView: scan_again invoked')
#
#         start_scanning()
#         Clock.schedule_once(self.update_list_devices, 8)
#
#     def update_list_devices(self, *args):
#         Logger.info('SettingsView: updating list of devices')
#
#         self.ids.set_scanned_devices_list_grid.clear_widgets()
#
#         for _urls_settings_list_item in scanned_online_urls:
#
#             self.formated_dev_name_address = '{}/{}'.format(_urls_settings_list_item, scanned_online_urls[_urls_settings_list_item])
#
#             self.ids.set_scanned_devices_list_grid.add_widget(SettingsViewItem(self.formated_dev_name_address))
#
#     def save_settings(self, *args):
#         if self.choosen_device:
#             Logger.info('save settings set_as_host {}'.format(self.choosen_device))
#
#             self.settings_set_as_host(self.choosen_device)
#
#     def settings_set_as_host(self, host_in):
#         breaker = host_in.find('/')
#         prepare_url = host_in[:breaker]
#         Connector.url = prepare_url
#
#     def return_to_main_view(self, *args):
#         self.manager.current = 'main'


class LoginView(Screen):
    def __init__(self, **kwargs):
        super(LoginView, self).__init__(**kwargs)
        Logger.info('LoginView: Initialized {}'.format(self))

        self.name = 'LoginScreen'
        self.plex_inst = App.get_running_app().plex_inst

    def login_focus(self,  *args):
        self.close_plex_login_error()

        if args[0]:
            local_network_input_in_y_pos = 0.5
            puser_input_in_y_pos = 0.4
            ppass_input_in_y_pos = 0.3
        else:
            local_network_input_in_y_pos = 0.3
            puser_input_in_y_pos = 0.2
            ppass_input_in_y_pos = 0.1

        self.ids.local_network_input_in.pos_hint = {'center_x': 0.5, 'center_y': local_network_input_in_y_pos}
        self.ids.puser_input_in.pos_hint = {'center_x': 0.5, 'center_y': puser_input_in_y_pos}
        self.ids.ppass_input_in.pos_hint = {'center_x': 0.5, 'center_y': ppass_input_in_y_pos}

    @util_f.schedule_once_two_arg(timing=1)
    def get_plex(self, user_name, user_pass, *args):
        Logger.error('LoginView: Login Plex u: {} p: {}'.format(user_name, user_pass))

        try:
            scan_screen = ScanView(plex_server=self.plex_inst.get_servers_handler(user_n=user_name, user_p=user_pass))
            util_f.scm_switch_to_transition(self, scan_screen)
            Logger.info('LoginView: switching to ScanView')

        except Exception as e:
            self.show_plex_login_error()
            Logger.error('LoginView: Plex login failed due to {}'.format(e))

            pass

    def skip_login(self, *args):
        util_f.scm_switch_to_transition(self, MainView())
        util_f.busy_loading_overlay(0, 8)

    def show_plex_login_error(self):
        self.ids.ppass_input_in_er.opacity = 1
        self.ids.puser_input_in_er.opacity = 1

    def close_plex_login_error(self):
        self.ids.ppass_input_in_er.opacity = 0
        self.ids.puser_input_in_er.opacity = 0


class Progression(Screen):

    def __init__(self, **kwargs):
        super(Progression, self).__init__(**kwargs)
        Logger.info('Progression: Initialized {}'.format(self))

        self.plex_instance = App.get_running_app().plex_inst
        self.connector = App.get_running_app().connection_inst

        self.sch_event = Clock.schedule_interval(self.progression_bar_handler, c_i.pr_speed)

    def progression_bar_handler(self, *args):

        if self.ids.progress_bar_overlay_image_ti.size_hint_y < 1:
            self.ids.progress_bar_main_image.opacity += 0.01
            self.ids.progress_bar_overlay_image_t.size_hint_y -= 0.01
            self.ids.progress_bar_overlay_image_ti.size_hint_y += 0.01

        else:
            Logger.info('Progression: Progress bar scheduler event stopped')

            self.sch_event.cancel()
            self.skip_login()

    def skip_login(self):
        # check if plex credentials are stored and if server is stored
        # if true screen manager -> MainView and start busy overlay
        if self.plex_instance.check_stored_credentials() and self.plex_instance.check_stored_server():
            self.connector.url = self.plex_instance.get_stored_server()[1]
            util_f.scm_switch_to_transition(self, MainView())
            util_f.busy_loading_overlay(0, 8)
            Logger.info('Progression: switching to MainView')

        # check if only plex credentials are store if true screen manager -> ScanView and pass method which retrieves
        # either stored plex servers or does the api request
        elif self.plex_instance.check_stored_credentials():
            util_f.scm_switch_to_transition(self, ScanView(self.plex_instance.get_servers_handler()))
            Logger.info('Progression: switching to ScanView')

        else:
            util_f.scm_switch_to_transition(self, LoginView())
            Logger.info('Progression: switching to LoginView')


class ViewControl(ScreenManager):

    Logger.info('Window size {}'.format(Window.size))

    def __init__(self, **kwargs):
        super(ViewControl, self).__init__(**kwargs)
        Logger.info('ViewControl: Initialized {}'.format(self))

        self.media = App.get_running_app().media
        self.scheduled_start_progression()

        self.get_media_content(Movies(order='-1', sort='last added').get_search(), 2)
        self.get_media_content(Shows(order='-1', sort='updated').get_search(), 4)

    @util_f.schedule_once_no_args(timing=1)
    def scheduled_start_progression(self, *args):
        self.add_widget(Progression(name='loading'))

    @util_f.schedule_once_two_arg_timing(timing=None)
    def get_media_content(self, api_instance, *args):
        Logger.info('ViewControl: get_media_content invoked')

        """get inital latest movies and series, populate shows dictionary populate movies dicionary"""

        util_f._get_api(self, api_instance, self.media)


class LoaderAnimation(StencilView):
    def __init__(self, parent_widget, **kwargs):
        super(LoaderAnimation, self).__init__(**kwargs)
        Logger.info('LoaderAnimation: Initialized {}'.format(self))

        self.p_w = parent_widget
        self.size_hint = (None, None)
        self.size = self.p_w.size
        self.pos = self.p_w.pos
        self.ids.loader_animation_image.center_x = self.p_w.center_x
        self.ids.loader_animation_image.center_y = self.p_w.center_y

        self.sch_event = Clock.schedule_interval(self._start_animation, c_i.animation_interval)

    def _cancel_animation(self,*args):

        self.sch_event.cancel()
        Logger.info('LoaderAnimation: animation canceled {}'.format(self))

    def _start_animation(self, *args):

        self.size[1] -= c_i.animation_height_decrese
        # Logger.info('LoaderAnimation: animation started {}'.format(self))


class LoaderOverlay(ModalView):

    def __init__(self, **kwargs):
        super(LoaderOverlay, self).__init__(**kwargs)
        Logger.info('LoaderOverlay: Initialized {}'.format(self))

        self.size = (c_i.height_x / 1.5, c_i.height_x / 1.5)

    def reset_on_dismiss(self, *args):
        # Logger.info('LoaderOverlay: child class of animation {}'.format(self.children[0].children[0]))
        # Logger.info('LoaderOverlay: child class of animation {}'.format(self.children[0]))
        try:
            self.ids.lo_container.children[0]._cancel_animation()
        except Exception as e:
            Logger.info('animation fail {}'.format(e))
            pass
        self.ids.lo_container.clear_widgets()

    def _add_animation_on_enter(self, *args):
        self.ids.lo_container.add_widget(LoaderAnimation(self.ids.lo_container))


class CommandStatus(ModalView):

    def __init__(self, **kwargs):
        super(CommandStatus, self).__init__(**kwargs)
        Logger.info('CommandStatus: Initialized {}'.format(self))

        self.size = (c_i.height_x / 1.5, c_i.height_x / 1.5)


class ConnectionErrorPopup(Popup):

    def __init__(self, **kwargs):
        super(ConnectionErrorPopup, self).__init__(**kwargs)
        Logger.info('ConnectionErrorPopup: Initialized {}'.format(self))

        self.size = (c_i.height_x / 1.5, c_i.height_x / 1.5)

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
        self.command_status = CommandStatus()
        self.conn_error_popup = ConnectionErrorPopup()
        self.connection_inst = c_i.Connector()
        self.plex_inst = Plex()
        self.network_inst = Network()
        self.media = Media()
        self.filter = Filter()
        self.favourites = Favourites()
        self.filter_modal = FilterModalView()
        Cache.register('screen_cache', limit=10, timeout=c_i.CACHE_TIME)
        Logger.debug('Application: Created Cache object {}'.format(Cache))

        return self.root

    def on_start(self):
        try:
            self.root.add_widget(ViewControl())
        except Exception as e:
            Logger.error('Application; Failed due to {}'.format(e))

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
