
from kivy.app import App
from kivy.cache import Cache
from kivy.properties import partial
from kivy import Logger
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.utils import get_color_from_hex
from functools import wraps

import constant_instance as c_i
from api import Movies, Shows, get_api


def start_loade(x, *args):

    App.get_running_app().loader_overlay.open(animation=True)
    Logger.info('start loader for {}'.format(x))


def stop_loade(x, *args):
    App.get_running_app().loader_overlay.dismiss()
    Logger.info('stop loader for {}'.format(x))


def _get_api(parent_instance, _payload, _db):
    # type: (object, object, object) -> object
    try:
        get_api(_payload, _db)
        Logger.info('{}: get_media_content success'.format(parent_instance))

    except Exception as e:
        Logger.error('{}: get_media_content fail due to {}'.format(parent_instance, e))

        App.get_running_app().conn_error_popup.open()
        pass


def sf(db_instance, hash_key, type_key, json_val, *args):

    if args[0]._favourite:

        db_instance._delete(key=hash_key)
        args[0]._favourite = False
        args[1].background_normal = "./images/favno.png"

    else:
        db_instance._put(key=hash_key, val_second=type_key, val=json_val)
        args[0]._favourite = True
        args[1].background_normal = "./images/fav.png"


def sch_w(self_instance, to_w, w, tim, *args):
    if tim == 0:
        timing = 0
    else:
        timing = tim/2

    Clock.schedule_once(partial(add_w, self_instance, to_w, w), timing)


def add_w(self_instance, to_w, w, *args):
    to_w.add_widget(w)
    self_instance.animation.start(w)


def add_item_w(_instance, hash_map, item_w_instance, _layout, change_function, type=None, counter_limit=None, favourites=None, addi_ch=None, _widget_=None,  _media_db=None, _favourites_db=None):
    _count = 0

    for _key in hash_map:
        if _count < counter_limit:

            _is_favourite = _favourites_db._exists(_key)

            if favourites:
                _jsoned = _favourites_db._get(key=_key)

                favourite_type = _favourites_db._get(key=_key, child_key='val_second')
            else:
                _jsoned = hash_map[_key]

            if _jsoned:
                _instance._item_instance = item_w_instance(_jsoned['_id'], _is_favourite)
                _instance._item_instance.size = (0, 0)
                _instance._item_instance.ids.item_im_holder_float_b.bind(
                    on_press=partial(sf, _favourites_db, _key, type,
                                     _jsoned, _instance._item_instance))

                if _is_favourite:
                    _instance._item_instance.ids.item_im_holder_float_b.background_normal = './images/fav.png'

                try:
                    _instance._item_instance.ids.item_im_holder_float_i.source = _jsoned['images'][
                        'poster'].replace('https', 'http')

                except Exception:
                    Logger.info('No image setting default')
                    _instance._item_instance.ids.item_im_holder_float.remove_widget(_instance._item_instance.ids.item_im_holder_float_i)
                    _instance._item_instance.ids.item_im_holder_float.add_widget(
                        Image(source='images/logo.png', pos_hint={'center_x': 0.5, 'center_y': .5}))
                    pass

                _instance._item_instance.ids.item_title_b.text = _jsoned['title']
                _instance._item_instance.ids.item_title_b.text_size = (((c_i.width_x / 3) - 45), None)

                if favourites:
                    if favourite_type == 'show':
                        _instance._item_instance.ids.item_title_b.bind(
                        on_release=lambda x, arg1=_instance, arg2=_instance._item_instance.megs, arg3=_favourites_db , arg4=_widget_: change_function(x, arg1, arg2, arg3, arg4))
                    else:
                        _instance._item_instance.ids.item_title_b.bind(
                            on_release=lambda x, arg1=_instance, arg2=_instance._item_instance.megs, arg3=_favourites_db , arg4=_widget_: addi_ch(x, arg1, arg2, arg3, arg4))
                else:

                    _instance._item_instance.ids.item_title_b.bind(
                        on_release=lambda x, arg1=_instance, arg2=_instance._item_instance.megs, arg3=_media_db , arg4=_widget_: change_function(x, arg1, arg2, arg3, arg4))

                sch_w(_instance, _layout, _instance._item_instance, _count)

                _count += 1


def create_scroll_view(scroll_w, scroll_h, on_scroll_a=None, on_scroll_ar=None, cols=3):
    grid_layout = c_i.ScrollGrid(cols)

    grid_layout.bind(minimum_height=grid_layout.setter('height'))

    scroll_list = c_i.ScrollV(scroll_w, scroll_h, on_scroll_a=on_scroll_a, on_scroll_ar=on_scroll_ar)

    scroll_list.add_widget(grid_layout)

    return scroll_list, grid_layout


def add_widget_with_loading(_add_method, parent_instance=None, _func_arg=None):

    Clock.schedule_once(start_loade, int(c_i.w_l_start))

    if _func_arg:
        Clock.schedule_once(lambda x: _add_method(parent_instance, _func_arg), 0.5)
    else:
        Clock.schedule_once(_add_method, 0.5)
    Clock.schedule_once(stop_loade, int(c_i.w_l_stop))


def busy_loading_overlay(entry, finish):
    Logger.critical('Busy loader started')
    Clock.schedule_once(start_loade, entry)
    Clock.schedule_once(stop_loade, finish)


def start_command_status_info(status, *args):

    if status == 'downloading':
        App.get_running_app().command_status.ids.command_status_info_i_holder.source = './images/downl.png'
    elif status == 'playing':
        App.get_running_app().command_status.ids.command_status_info_i_holder.source = './images/play.png'
    else:
        App.get_running_app().command_status.ids.command_status_info_i_holder.source = './images/no_connection.png'

    App.get_running_app().command_status.open()


def stop_command_status_info(instance, *args):
    App.get_running_app().command_status.dismiss()
    Logger.info('stop command status info for {}'.format(instance))


def command_status_info(entry, finish, status):
    Clock.schedule_once(partial(start_command_status_info, status), entry)
    Clock.schedule_once(stop_command_status_info, finish)


def change_to_series_single(_b, instance, __show_id, _dict_d, _wid_inst, *args):
    Logger.info('{}: change_to_series_single {}'.format(instance, __show_id))
    add_widget_with_loading(add_scms, parent_instance=instance, _func_arg=[__show_id, _dict_d, _wid_inst])


def change_to_movies_single(_b, instance, __movie_id, _dict_d, _wid_inst, *args):
    Logger.info('{}: change_to_movies_single {}'.format(instance, __movie_id))
    add_widget_with_loading(add_scmm, parent_instance=instance, _func_arg=[__movie_id, _dict_d, _wid_inst])


def add_scms(self, list, *args):
    __s_id = list[0]
    _dict_d = list[1]
    _wid = list[2]

    _get_api(self, Shows(_id=__s_id).get_search_by_id(), _dict_d)

    self.manager.add_widget(_wid(__s_id))
    self.manager.current = 'svms'


def add_scmm(self, list, *args):
    __m_id = list[0]
    _dict_d = list[1]
    _wid = list[2]

    _get_api(self, Movies(_id=__m_id).get_search_by_id(), _dict_d)

    self.manager.add_widget(_wid(__m_id))
    self.manager.current = 'mvms'

##### SCHEDULER DECORATOR #####


def schedule_once_no_args(timing=1):

    def scheduled_decorator(func):
        @wraps(func)
        def wrapped_f(*args, **kwargs):
            Logger.info('schedule_once_no_args Decorator with args {} and timing {}'.format(args, timing))
            return Clock.schedule_once(partial(func, args[0]), timing)

        return wrapped_f
    return scheduled_decorator


def schedule_once_one_arg(timing=1):

    def inner_function(func):

        def wrapper(*args, **kwargs):
            Logger.info('schedule_once_one_arg Decorator with args {} and timing {}'.format(args, timing))
            Clock.schedule_once(partial(func, args[0], args[1]), timing)

        return wrapper

    return inner_function


def schedule_once_two_arg(timing=1):

    def inner_function(func):

        def wrapper(*args, **kwargs):
            Logger.info('schedule_once_one_arg Decorator with args {} and timing {}'.format(args, timing))

            Clock.schedule_once(partial(func, args[0], args[1], args[2]), timing)

        return wrapper

    return inner_function


def schedule_once_two_arg_timing(timing=1):

    def inner_function(func):

        def wrapper(*args, **kwargs):
            Logger.info('schedule_once_one_arg Decorator with args {} and timing {}'.format(args, args[2]))

            Clock.schedule_once(partial(func, args[0], args[1]), args[2])

        return wrapper

    return inner_function


def _add_navigation_buttons(_class_intance, _b_class):
    for i in c_i.navigation_buttons:
        x = _b_class(i)
        x.bind(on_press=partial(_class_intance.set_as_current_screen, c_i.navigation_buttons[i]))
        _class_intance.main_nav_p.add_widget(x)
        if i == 'Latest':
            x.state = 'down'


def _paginator_buton_call(self, *args):

    self.holder.remove_widget(self.holder.children[0])

    x_sort = self.filt._get('sort')
    x_order = self.filt._get('order')
    x_genre = self.filt._get('genre')

    if not x_order or x_order is None:

        x_order = '-1'
        Logger.info('{}: _filter_order setting to default {}"'.format(self._par_inst, x_order))

    if not x_sort or x_sort is None:

        if self._type == 'm':
            x_sort = 'last added'
        else:
            x_sort = 'updated'

        Logger.info('{}: _filter_sort setting to default {}'.format(self._par_inst, x_sort))

    if not x_genre or x_genre is None:

        x_genre = None
        Logger.info('{}: _filter_genre setting to default {}'.format(self._par_inst, x_genre))

    if self._type == 'm':
        _get_api(self, Movies(page=self.text, order=x_order, sort=x_sort, genre=x_genre).get_search(), self._db_d)
    else:
        _get_api(self, Shows(page=self.text, order=x_order, sort=x_sort, genre=x_genre).get_search(), self._db_d)

    self.holder.add_widget(self.screen_manager_inst(self._par_inst))


def create_scroll_view_horizontal(columns=None):
    grid_layout = c_i.ScrollGridHorizontal(cols=columns)

    grid_layout.bind(minimum_width=grid_layout.setter('width'))

    scroll_list = c_i.ScrollVHorizontal()

    return scroll_list, grid_layout


def scm_switch_to_transition(_self_instance, screen, duration=2):
    _self_instance.manager.switch_to(screen, transition=c_i.TRANSITION(), duration=duration)


def sch_ref(self, parent, *args):
    # Logger.error('self {}'.format(self))#scroll view instance iz koje se izvlaci scroll_y
    # Logger.error('self scroll y{}'.format(self.scroll_y))
    # Logger.error('self parent holder {}'.format(parent.parent_hold))#view main instanca pristup parent holder box
    #
    # Logger.error('parent {}'.format(parent))#view main instanca
    # Logger.error('arg {}'.format(args))
    #

    if not parent.refreshed:
        if self.scroll_y == 0.0:
            refresh_on_scroll(parent)
            parent.refreshed = True
    else:
        Logger.info('FavouritesViewMain: refresh done')


def refresh_on_scroll(parent, *args):
    Logger.info('FavouritesView: refresh invoked {}'.format(parent))

    parent.parent_hold.clear_widgets()
    parent.parent_hold.add_widget(parent.instance_to_add(parent.parent_hold))


def clear_widgets(widget_id):
    Logger.info('{}: cleaner'.format(widget_id))

    widget_id.clear_widgets()


def resolve_enter_screen(self, sc_cache, wid_id, child_class):
    Logger.info('{}: on enter'.format(self))

    if not Cache.get('screen_cache', sc_cache):
        clear_widgets(wid_id)
        wid_id.add_widget(child_class(wid_id))
    else:
        Logger.debug('{}: {} already exists'.format(self, child_class))

# _instance, hash_map, item_w_instance, _layout, change_function, type=None, counter_limit=None, favourites=None, addi_ch=None, _widget_=None,  _media_db=None, _favourites_db=None

def set_modal_size(self):
    self.size = (c_i.height_x / 1.5, c_i.height_x / 1.5)


class Episode:
    # def __init__(self, overview, episode, season, tor, title, imdb_id):
    def __init__(self):

        # self.overview = overview
        # self.episode = episode
        # self.season = season
        # self.tor = tor
        # self. title = title
        # self.imdb_id = imdb_id
        self.overview = None
        self.episode = None
        self.season = None
        self.tor = None
        self.title = None
        self.imdb_id = None
        self.torrents = None

        # print(dir(self))

def add_item_ser_single(self):
    did = {
        # '1' : [{'1': object}, {'2': object}],
        # '2': [{'1': object}, {'2': object}],


    }
    # for i in did:
    #     print(i)
    #     print(did[i])
    #     for z in did[i]:
    #         print(z)
    #         for b in z:
    #             print(b)
    #             print(z[b])
    #
    for _key in self:
        # print('{} --> {}'.format(_key, self[_key]))
        if _key == 'episodes':

            for i in self[_key]:
                krok = Episode()

                # print(' i {} '.format(i))
                for z in i:
                    # print('{} --> {}'.format(z, i[z]))

                    if 'title' in z:
                        # print('title --> {}'.format(i[z]))
                        krok.title = i[z]
                    elif 'season' in z:
                        # print('season --> {}'.format(i[z]))
                        krok.season = i[z]
                    elif 'episode' in z:
                        # print('episode --> {}'.format(i[z]))
                        krok.episode = i[z]

                    elif 'overview' in z:
                        # print('overview --> {}'.format(i[z]))
                        krok.overview = i[z]

                    elif 'tvdb_id' in z:
                        # print('tvdb_id --> {}'.format(i[z]))
                        krok.imdb_id = i[z]

                    elif 'torrents' in z:
                        krok.torrents = i[z]

                        # print('')
                        # print('torrent --> {}'.format(i[z]))
                try:
                    # print(krok.season)
                    if did[krok.season]:
                        x=9
                        # print(krok.season)
                        # print('postiji')
                except KeyError:
                    did[krok.season] = []
                did[krok.season].append({krok.episode: krok})
                # print('<<<<<<<<<>>>>>>>>>>')

                # print(krok.title)
                # print(krok.imdb_id)
                # print(krok.overview)
                # print(krok.season)
                # print(krok.episode)
                # print('<<<<<<<<<>>>>>>>>>>')
    # print(did)
    for i in did:
        print('Season {}'.format(i))
        for k in did[i]:
            for b in k:
                print('-------Episode {}'.format(b))
                print('--------------Title {}'.format(k[b].title))
                print('--------------Overview {}'.format(k[b].overview))
                print('--------------Season {}'.format(k[b].season))
                print('--------------Episode {}'.format(k[b].episode))
                print('--------------IMDB_ID {}'.format(k[b].imdb_id))
                print('--------------Torrents {}'.format(k[b].torrents))




        # for show_node in hash_map[_key]:
        #
        #     if show_node == 'episodes':
        #         self.episode_count = int(len(hashed_dic_show[_single_show_item_in_dic]['episodes']))
        #         self.accord_height = dp((1 * 44) + 340)
        #
        #         self._single_show_accordion = Accordion(orientation='vertical', height=self.accord_height,
        #                                                 size_hint_y=None, min_space=dp(44))
        #
        #         self._single_show_accordion.id = 'testAccordian'
        #
        #         self.g_scroll_list = ScrollView(size_hint=(None, None),
        #                                         size=(c_i.width_x - 40, c_i.height_x * 0.4),
        #                                         on_scroll_move=self.sch_lazy,
        #                                         pos_hint={'center_x': 0.5, 'center_y': 0.5})
        #
        #         self.ids.series_view_main_single_container_se.add_widget(self.g_scroll_list)
        #         self.g_scroll_list.add_widget(self._single_show_accordion)
        #
        #         Logger.info('SeriesViewMainSingle: Show level >>>>>')
        #
        #         Logger.info(
        #             'SeriesViewMainSingle: Show title {}'.format(hashed_dic_show[_single_show_item_in_dic]['title']))
        #         _show_t = str(hashed_dic_show[_single_show_item_in_dic]['title']).encode('utf-8')
        #         self.ids.series_view_main_single_nav_title_t.text = str(_show_t)
        #
        #         Logger.info(
        #             'SeriesViewMainSingle: Show year {}'.format(hashed_dic_show[_single_show_item_in_dic]['year']))
        #         _show_y = str(hashed_dic_show[_single_show_item_in_dic]['year'])
        #         _show_y = _show_y.encode('utf-8')
        #
        #         # Logger.info(' Show synopsis {}'.format(hashed_dic_show[_single_show_item_in_dic]['synopsis']))
        #         _show_s = hashed_dic_show[_single_show_item_in_dic]['synopsis']
        #         _show_s = _show_s.encode('utf-8')
        #
        #         Logger.info('SeriesViewMainSingle: Show runtime {}'.format(
        #             hashed_dic_show[_single_show_item_in_dic]['runtime']))
        #         _show_r = str(hashed_dic_show[_single_show_item_in_dic]['runtime'])
        #         _show_r = _show_r.encode('utf-8')
        #
        #         try:
        #             Logger.info('SeriesViewMainSingle: Show image {}'.format(
        #                 hashed_dic_show[_single_show_item_in_dic]['images']['poster'].replace('https', 'http')))
        #             _show_im = str(hashed_dic_show[_single_show_item_in_dic]['images']['poster'])
        #             _show_im = _show_im.replace('https', 'http')
        #         except KeyError:
        #             Logger.warning('SeriesViewMainSingle: Show image fallback{}')
        #             _show_im = './images/logo.png'
        #             pass
        #
        #         Logger.info(
        #             'SeriesViewMainSingle: Show status {}'.format(hashed_dic_show[_single_show_item_in_dic]['status']))
        #         _show_st = str(hashed_dic_show[_single_show_item_in_dic]['status'])
        #         _show_st = _show_st.encode('utf-8')
        #
        #         Logger.info('SeriesViewMainSingle: Show number of episodes {}'.format(
        #             len(hashed_dic_show[_single_show_item_in_dic]['episodes'])))
        #         self._ep_num = len(hashed_dic_show[_single_show_item_in_dic]['episodes'])
        #
        #         self.ids.series_view_main_single_container.add_widget(
        #             SeriesViewMainSingleTop(_show_y, _show_s, _show_r, _show_im, _show_st))
        #         lok = 0
        #         for _episode_node in hashed_dic_show[_single_show_item_in_dic][show_node]:
        #             lok += 1
        #             acc_item = AccordionItem(collapse=True, orientation='vertical', background_normal='./images/ti.png',
        #                                      background_selected='./images/ti.png')
        #
        #             acc_item.container.orientation = 'vertical'
        #             Logger.info('SeriesViewMainSingle: Episode level >>>>>')
        #             # Logger.info(z)
        #             try:
        #                 Logger.info('SeriesViewMainSingle: Episode title {}'.format(_episode_node['title']))
        #             except UnicodeEncodeError:
        #                 pass
        #
        #             if _episode_node['title']:
        #                 ti = _episode_node['title'].encode('utf-8')
        #                 if len(ti) > 42:
        #                     ti = '{}...'.format(ti[:41])
        #             else:
        #                 ti = ''
        #
        #             Logger.info('SeriesViewMainSingle: Episode overview')
        #             if _episode_node['overview']:
        #                 _show_episode_over = _episode_node['overview']
        #                 _show_episode_over = _show_episode_over.encode('utf-8')
        #                 Logger.info('SeriesViewMainSingle: Episode overview {}'.format(_show_episode_over))
        #             else:
        #                 _show_episode_over = ''
        #
        #             Logger.info('SeriesViewMainSingle: Episode episode number {}'.format(_episode_node['episode']))
        #             _show_episode = str(_episode_node['episode'])
        #             _show_episode = _show_episode.encode('utf-8')
        #
        #             Logger.info('SeriesViewMainSingle: Episode season number {}'.format(_episode_node['season']))
        #             _show_season = str(_episode_node['season'])
        #             _show_season = _show_season.encode('utf-8')
        #
        #             acc_item.title = '{} {} {}'.format(ti, _show_season, _show_episode)
        #
        #             _show_accordion_item_container_synopsis = ShowEpSyn(str(_show_episode_over))
        #
        #             acc_item.container.add_widget(_show_accordion_item_container_synopsis)
        #
        #             acc_item.container.add_widget(Tor(_episode_node['torrents'], self.series_single_connector))
        #
        #             self.buffe.append(acc_item)
        #
        #             if lok < 5:
        #                 self.lazyy()
l={'_id': 'tt4574334', 'imdb_id': 'tt4574334', 'tvdb_id': '305288', 'title': 'Stranger Things', 'year': '2016', 'slug': 'stranger-things', 'synopsis': 'When a young boy disappears, his mother, a police chief, and his friends must confront terrifying forces in order to get him back.', 'runtime': '50', 'country': 'us', 'network': 'Netflix', 'air_day': 'Friday', 'air_time': '03:00', 'status': 'returning series', 'num_seasons': 3, 'last_updated': 1562374628879, '__v': 0, 'episodes': [{'torrents': {'0': {'provider': 'EZTV', 'peers': 0, 'seeds': 0, 'url': 'magnet:?xt=urn:btih:4ea12380f7daaabbfb56fd03475b8b9b1c2c6bc2&dn=Stranger.Things.S03E01.480p.x264-mSD%5Beztv%5D.mkv%5Beztv%5D&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A80&tr=udp%3A%2F%2Fglotorrents.pw%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Fexodus.desync.com%3A6969'}, '720p': {'provider': 'EZTV', 'peers': 0, 'seeds': 0, 'url': 'magnet:?xt=urn:btih:8cb8f7ac234bb8ccf7d983cfee36837e0773a55f&dn=Stranger.Things.S03E01.720p.WEBRip.X264-METCON%5Beztv%5D.mkv%5Beztv%5D&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A80&tr=udp%3A%2F%2Fglotorrents.pw%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Fexodus.desync.com%3A6969'}, '480p': {'provider': 'EZTV', 'peers': 0, 'seeds': 0, 'url': 'magnet:?xt=urn:btih:4ea12380f7daaabbfb56fd03475b8b9b1c2c6bc2&dn=Stranger.Things.S03E01.480p.x264-mSD%5Beztv%5D.mkv%5Beztv%5D&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A80&tr=udp%3A%2F%2Fglotorrents.pw%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Fexodus.desync.com%3A6969'}}, 'watched': {'watched': False}, 'first_aired': 1562223600, 'date_based': False, 'overview': "Summer brings new jobs and budding romance. But the mood shifts when Dustin's radio picks up a Russian broadcast, and Will senses something is wrong.", 'title': 'Chapter One: Suzie, Do You Copy?', 'episode': 1, 'season': 3, 'tvdb_id': 6933995}, {'torrents': {'0': {'provider': 'EZTV', 'peers': 0, 'seeds': 0, 'url': 'magnet:?xt=urn:btih:9b823be197c1b4c6d6533a19b9e1ac3b60785ade&dn=Stranger.Things.S03E02.480p.x264-mSD%5Beztv%5D.mkv%5Beztv%5D&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A80&tr=udp%3A%2F%2Fglotorrents.pw%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Fexodus.desync.com%3A6969'}, '720p': {'provider': 'EZTV', 'peers': 0, 'seeds': 0, 'url': 'magnet:?xt=urn:btih:0cddf7743a76f49106b579ceabc45659fb86a983&dn=Stranger.Things.S03E02.720p.WEBRip.X264-METCON%5Beztv%5D.mkv%5Beztv%5D&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A80&tr=udp%3A%2F%2Fglotorrents.pw%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Fexodus.desync.com%3A6969'}, '480p': {'provider': 'EZTV', 'peers': 0, 'seeds': 0, 'url': 'magnet:?xt=urn:btih:9b823be197c1b4c6d6533a19b9e1ac3b60785ade&dn=Stranger.Things.S03E02.480p.x264-mSD%5Beztv%5D.mkv%5Beztv%5D&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A80&tr=udp%3A%2F%2Fglotorrents.pw%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Fexodus.desync.com%3A6969'}}, 'watched': {'watched': False}, 'first_aired': 1562223600, 'date_based': False, 'overview': 'Nancy and Jonathan follow a lead, Steve and Robin sign on to a secret mission, and Max and Eleven go shopping. A rattled Billy has troubling visions.', 'title': 'Chapter Two: The Mall Rats', 'episode': 2, 'season': 3, 'tvdb_id': 6933996}, {'torrents': {'0': {'provider': 'EZTV', 'peers': 0, 'seeds': 0, 'url': 'magnet:?xt=urn:btih:399833fd100f21c696599b0f68716ddc14dc9a39&dn=Stranger.Things.S03E03.480p.x264-mSD%5Beztv%5D.mkv%5Beztv%5D&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A80&tr=udp%3A%2F%2Fglotorrents.pw%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Fexodus.desync.com%3A6969'}, '720p': {'provider': 'EZTV', 'peers': 0, 'seeds': 0, 'url': 'magnet:?xt=urn:btih:3370e6e2ff88fe42a00efcb5bfb27ce072cd662e&dn=Stranger.Things.S03E03.720p.WEBRip.X264-METCON%5Beztv%5D.mkv%5Beztv%5D&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A80&tr=udp%3A%2F%2Fglotorrents.pw%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Fexodus.desync.com%3A6969'}, '480p': {'provider': 'EZTV', 'peers': 0, 'seeds': 0, 'url': 'magnet:?xt=urn:btih:399833fd100f21c696599b0f68716ddc14dc9a39&dn=Stranger.Things.S03E03.480p.x264-mSD%5Beztv%5D.mkv%5Beztv%5D&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A80&tr=udp%3A%2F%2Fglotorrents.pw%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Fexodus.desync.com%3A6969'}}, 'watched': {'watched': False}, 'first_aired': 1562223600, 'date_based': False, 'overview': 'With El and Max looking for Billy, Will declares a day without girls. Steve and Dustin go on a stakeout, and Joyce and Hopper return to Hawkins Lab.', 'title': 'Chapter Three: The Case of the Missing Lifeguard', 'episode': 3, 'season': 3, 'tvdb_id': 6933997}, {'torrents': {'0': {'provider': 'EZTV', 'peers': 0, 'seeds': 0, 'url': 'magnet:?xt=urn:btih:f5cbec378189500a87d568ec861de048d6bea585&dn=Stranger.Things.S03E04.480p.x264-mSD%5Beztv%5D.mkv%5Beztv%5D&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A80&tr=udp%3A%2F%2Fglotorrents.pw%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Fexodus.desync.com%3A6969'}, '720p': {'provider': 'EZTV', 'peers': 0, 'seeds': 0, 'url': 'magnet:?xt=urn:btih:3e79649d2cc8b2e83d603f6b28b68d46f9723742&dn=Stranger.Things.S03E04.720p.WEBRip.X264-METCON%5Beztv%5D.mkv%5Beztv%5D&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A80&tr=udp%3A%2F%2Fglotorrents.pw%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Fexodus.desync.com%3A6969'}, '480p': {'provider': 'EZTV', 'peers': 0, 'seeds': 0, 'url': 'magnet:?xt=urn:btih:f5cbec378189500a87d568ec861de048d6bea585&dn=Stranger.Things.S03E04.480p.x264-mSD%5Beztv%5D.mkv%5Beztv%5D&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A80&tr=udp%3A%2F%2Fglotorrents.pw%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Fexodus.desync.com%3A6969'}}, 'watched': {'watched': False}, 'first_aired': 1562223600, 'date_based': False, 'overview': 'A code red brings the gang back together to face a frighteningly familiar evil. Karen urges Nancy to keep digging, and Robin finds a useful map.', 'title': 'Chapter Four: The Sauna Test', 'episode': 4, 'season': 3, 'tvdb_id': 6933998}, {'torrents': {'0': {'provider': 'EZTV', 'peers': 0, 'seeds': 0, 'url': 'magnet:?xt=urn:btih:1f6159a48802c1975fa8eaa52abe6e8d338b4535&dn=Stranger.Things.S03E05.480p.x264-mSD%5Beztv%5D.mkv%5Beztv%5D&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A80&tr=udp%3A%2F%2Fglotorrents.pw%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Fexodus.desync.com%3A6969'}, '720p': {'provider': 'EZTV', 'peers': 0, 'seeds': 0, 'url': 'magnet:?xt=urn:btih:b4b16e3d02443fa00a616737f88edf516b8b65d3&dn=Stranger.Things.S03E05.720p.WEBRip.X264-METCON%5Beztv%5D.mkv%5Beztv%5D&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A80&tr=udp%3A%2F%2Fglotorrents.pw%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Fexodus.desync.com%3A6969'}, '480p': {'provider': 'EZTV', 'peers': 0, 'seeds': 0, 'url': 'magnet:?xt=urn:btih:1f6159a48802c1975fa8eaa52abe6e8d338b4535&dn=Stranger.Things.S03E05.480p.x264-mSD%5Beztv%5D.mkv%5Beztv%5D&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A80&tr=udp%3A%2F%2Fglotorrents.pw%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Fexodus.desync.com%3A6969'}}, 'watched': {'watched': False}, 'first_aired': 1562223600, 'date_based': False, 'overview': 'Strange surprises lurk inside an old farmhouse and deep beneath the Starcourt Mall. Meanwhile, the Mind Flayer is gathering strength.', 'title': 'Chapter Five: The Flayed', 'episode': 5, 'season': 3, 'tvdb_id': 6934000}, {'torrents': {'0': {'provider': 'EZTV', 'peers': 0, 'seeds': 0, 'url': 'magnet:?xt=urn:btih:f80803929c88583a1825eb8836fe39e9ed6fbcad&dn=Stranger.Things.S03E06.480p.x264-mSD%5Beztv%5D.mkv%5Beztv%5D&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A80&tr=udp%3A%2F%2Fglotorrents.pw%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Fexodus.desync.com%3A6969'}, '720p': {'provider': 'EZTV', 'peers': 0, 'seeds': 0, 'url': 'magnet:?xt=urn:btih:f1ce80a3595b52c5653bb86bb4652e5199837a34&dn=Stranger.Things.S03E06.720p.WEBRip.X264-METCON%5Beztv%5D.mkv%5Beztv%5D&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A80&tr=udp%3A%2F%2Fglotorrents.pw%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Fexodus.desync.com%3A6969'}, '480p': {'provider': 'EZTV', 'peers': 0, 'seeds': 0, 'url': 'magnet:?xt=urn:btih:f80803929c88583a1825eb8836fe39e9ed6fbcad&dn=Stranger.Things.S03E06.480p.x264-mSD%5Beztv%5D.mkv%5Beztv%5D&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A80&tr=udp%3A%2F%2Fglotorrents.pw%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Fexodus.desync.com%3A6969'}}, 'watched': {'watched': False}, 'first_aired': 1562223600, 'date_based': False, 'overview': 'Dr. Alexei reveals what the Russians have been building, and Eleven sees where Billy has been. Dustin and Erica stage a daring rescue.', 'title': 'Chapter Six: E Pluribus Unum', 'episode': 6, 'season': 3, 'tvdb_id': 6934001}, {'torrents': {'0': {'provider': 'EZTV', 'peers': 0, 'seeds': 0, 'url': 'magnet:?xt=urn:btih:27bc43954550b168566a117f5ed1cceaa6301c26&dn=Stranger.Things.S03E07.480p.x264-mSD%5Beztv%5D.mkv%5Beztv%5D&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A80&tr=udp%3A%2F%2Fglotorrents.pw%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Fexodus.desync.com%3A6969'}, '720p': {'provider': 'EZTV', 'peers': 0, 'seeds': 0, 'url': 'magnet:?xt=urn:btih:55cdab9646b40f7b25053ede3a8bd7dbf195deff&dn=Stranger.Things.S03E07.720p.WEBRip.X264-METCON%5Beztv%5D.mkv%5Beztv%5D&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A80&tr=udp%3A%2F%2Fglotorrents.pw%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Fexodus.desync.com%3A6969'}, '480p': {'provider': 'EZTV', 'peers': 0, 'seeds': 0, 'url': 'magnet:?xt=urn:btih:27bc43954550b168566a117f5ed1cceaa6301c26&dn=Stranger.Things.S03E07.480p.x264-mSD%5Beztv%5D.mkv%5Beztv%5D&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A80&tr=udp%3A%2F%2Fglotorrents.pw%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Fexodus.desync.com%3A6969'}}, 'watched': {'watched': False}, 'first_aired': 1562223600, 'date_based': False, 'overview': "With time running out -- and an assassin close behind -- Hopper's crew races back to Hawkins, where El and the kids are preparing for war.", 'title': 'Chapter Seven: The Bite', 'episode': 7, 'season': 3, 'tvdb_id': 6934002}, {'torrents': {'0': {'provider': 'EZTV', 'peers': 0, 'seeds': 0, 'url': 'magnet:?xt=urn:btih:13938f71a22c4fb4efe112ba76a343a9ea7b33cc&dn=Stranger.Things.S03E08.480p.x264-mSD%5Beztv%5D.mkv%5Beztv%5D&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A80&tr=udp%3A%2F%2Fglotorrents.pw%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Fexodus.desync.com%3A6969'}, '720p': {'provider': 'EZTV', 'peers': 0, 'seeds': 0, 'url': 'magnet:?xt=urn:btih:a85d20f47f547b3da2e95d716b35119fbb668aa0&dn=Stranger.Things.S03E08.720p.WEBRip.X264-METCON%5Beztv%5D.mkv%5Beztv%5D&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A80&tr=udp%3A%2F%2Fglotorrents.pw%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Fexodus.desync.com%3A6969'}, '480p': {'provider': 'EZTV', 'peers': 0, 'seeds': 0, 'url': 'magnet:?xt=urn:btih:13938f71a22c4fb4efe112ba76a343a9ea7b33cc&dn=Stranger.Things.S03E08.480p.x264-mSD%5Beztv%5D.mkv%5Beztv%5D&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A80&tr=udp%3A%2F%2Fglotorrents.pw%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Fexodus.desync.com%3A6969'}}, 'watched': {'watched': False}, 'first_aired': 1562223600, 'date_based': False, 'overview': 'Terror reigns in the food court when the Mind Flayer comes to collect. But down below, in the dark, the future of the world is at stake.', 'title': 'Chapter Eight: The Battle of Starcourt', 'episode': 8, 'season': 3, 'tvdb_id': 6934003}, {'torrents': {'0': {'provider': 'ettv', 'peers': 2378, 'seeds': 1339, 'url': 'magnet:?xt=urn:btih:A2139C74CEDEBACA76681A6DCAA441EE4891561C&dn=stranger+things+s01e01+webrip+x264+turbo+ettv&tr=udp%3A%2F%2Ftracker.publicbt.com%2Fannounce&tr=udp%3A%2F%2Fglotorrents.pw%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A80%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce'}, '480p': {'provider': 'ettv', 'peers': 2378, 'seeds': 1339, 'url': 'magnet:?xt=urn:btih:A2139C74CEDEBACA76681A6DCAA441EE4891561C&dn=stranger+things+s01e01+webrip+x264+turbo+ettv&tr=udp%3A%2F%2Ftracker.publicbt.com%2Fannounce&tr=udp%3A%2F%2Fglotorrents.pw%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A80%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce'}}, 'watched': {'watched': False}, 'first_aired': 1468566000, 'date_based': False, 'overview': "On his way home from a friend's house, young Will sees something terrifying. Nearby, a sinister secret lurks in the depths of a government lab.", 'title': 'Chapter One: The Vanishing of Will Byers', 'episode': 1, 'season': 1, 'tvdb_id': 5468124}, {'torrents': {'0': {'url': 'magnet:?xt=urn:btih:CCBFAFDA2E64576B4BDA13B5566306CE92F80D1A&dn=stranger+things+s01e02+webrip+x264+turbo+ettv&tr=udp%3A%2F%2Ftracker.publicbt.com%2Fannounce&tr=udp%3A%2F%2Fglotorrents.pw%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A80%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce', 'seeds': 2859, 'peers': 3208, 'provider': 'ettv'}, '480p': {'url': 'magnet:?xt=urn:btih:CCBFAFDA2E64576B4BDA13B5566306CE92F80D1A&dn=stranger+things+s01e02+webrip+x264+turbo+ettv&tr=udp%3A%2F%2Ftracker.publicbt.com%2Fannounce&tr=udp%3A%2F%2Fglotorrents.pw%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A80%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce', 'seeds': 2859, 'peers': 3208, 'provider': 'ettv'}}, 'watched': {'watched': False}, 'first_aired': 1468566000, 'date_based': False, 'overview': 'Lucas, Mike and Dustin try to talk to the girl they found in the woods. Hopper questions an anxious Joyce about an unsettling phone call.', 'title': 'Chapter Two: The Weirdo on Maple Street', 'episode': 2, 'season': 1, 'tvdb_id': 5481194}, {'torrents': {'0': {'provider': 'ettv', 'peers': 1742, 'seeds': 905, 'url': 'magnet:?xt=urn:btih:C2B0712715EC40602EB4F10A56D395598D75405C&dn=stranger+things+s01e03+webrip+x264+turbo+ettv&tr=udp%3A%2F%2Ftracker.publicbt.com%2Fannounce&tr=udp%3A%2F%2Fglotorrents.pw%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A80%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce'}, '480p': {'provider': 'ettv', 'peers': 1742, 'seeds': 905, 'url': 'magnet:?xt=urn:btih:C2B0712715EC40602EB4F10A56D395598D75405C&dn=stranger+things+s01e03+webrip+x264+turbo+ettv&tr=udp%3A%2F%2Ftracker.publicbt.com%2Fannounce&tr=udp%3A%2F%2Fglotorrents.pw%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A80%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce'}}, 'watched': {'watched': False}, 'first_aired': 1468566000, 'date_based': False, 'overview': "An increasingly concerned Nancy looks for Barb and finds out what Jonathan's been up to. Joyce is convinced Will is trying to talk to her.", 'title': 'Chapter Three: Holly, Jolly', 'episode': 3, 'season': 1, 'tvdb_id': 5621926}, {'torrents': {'0': {'provider': 'ettv', 'peers': 1454, 'seeds': 802, 'url': 'magnet:?xt=urn:btih:DDD3C7DF65EDAA588730BA39FBA9F5B623389D46&dn=stranger+things+s01e04+webrip+x264+turbo+ettv&tr=udp%3A%2F%2Ftracker.publicbt.com%2Fannounce&tr=udp%3A%2F%2Fglotorrents.pw%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A80%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce'}, '480p': {'provider': 'ettv', 'peers': 1454, 'seeds': 802, 'url': 'magnet:?xt=urn:btih:DDD3C7DF65EDAA588730BA39FBA9F5B623389D46&dn=stranger+things+s01e04+webrip+x264+turbo+ettv&tr=udp%3A%2F%2Ftracker.publicbt.com%2Fannounce&tr=udp%3A%2F%2Fglotorrents.pw%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A80%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce'}}, 'watched': {'watched': False}, 'first_aired': 1468566000, 'date_based': False, 'overview': 'Refusing to believe Will is dead, Joyce tries to connect with her son. The boys give Eleven a makeover. Nancy and Jonathan form an unlikely alliance.', 'title': 'Chapter Four: The Body', 'episode': 4, 'season': 1, 'tvdb_id': 5621928}, {'torrents': {'0': {'provider': 'ettv', 'peers': 1116, 'seeds': 557, 'url': 'magnet:?xt=urn:btih:847E8CACDEB04929D3EB440475A44484CC5479D5&dn=stranger+things+s01e05+webrip+x264+turbo+ettv&tr=udp%3A%2F%2Ftracker.publicbt.com%2Fannounce&tr=udp%3A%2F%2Fglotorrents.pw%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A80%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce'}, '480p': {'provider': 'ettv', 'peers': 1116, 'seeds': 557, 'url': 'magnet:?xt=urn:btih:847E8CACDEB04929D3EB440475A44484CC5479D5&dn=stranger+things+s01e05+webrip+x264+turbo+ettv&tr=udp%3A%2F%2Ftracker.publicbt.com%2Fannounce&tr=udp%3A%2F%2Fglotorrents.pw%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A80%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce'}}, 'watched': {'watched': False}, 'first_aired': 1468566000, 'date_based': False, 'overview': 'Hopper breaks into the lab while Nancy and Jonathan confront the force that took Will. The boys ask Mr. Clarke how to travel to another dimension.', 'title': 'Chapter Five: The Flea and the Acrobat', 'episode': 5, 'season': 1, 'tvdb_id': 5621929}, {'torrents': {'0': {'provider': 'ettv', 'peers': 1019, 'seeds': 504, 'url': 'magnet:?xt=urn:btih:8FFF181BE63A75C0A4D5E6E230221E512E36C97A&dn=stranger+things+s01e06+webrip+x264+turbo+ettv&tr=udp%3A%2F%2Ftracker.publicbt.com%2Fannounce&tr=udp%3A%2F%2Fglotorrents.pw%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A80%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce'}, '480p': {'provider': 'ettv', 'peers': 1019, 'seeds': 504, 'url': 'magnet:?xt=urn:btih:8FFF181BE63A75C0A4D5E6E230221E512E36C97A&dn=stranger+things+s01e06+webrip+x264+turbo+ettv&tr=udp%3A%2F%2Ftracker.publicbt.com%2Fannounce&tr=udp%3A%2F%2Fglotorrents.pw%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A80%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce'}}, 'watched': {'watched': False}, 'first_aired': 1468566000, 'date_based': False, 'overview': "A frantic Jonathan looks for Nancy in the darkness, but Steve's looking for her, too. Hopper and Joyce uncover the truth about the lab's experiments.", 'title': 'Chapter Six: The Monster', 'episode': 6, 'season': 1, 'tvdb_id': 5621930}, {'torrents': {'0': {'provider': 'ettv', 'peers': 1081, 'seeds': 550, 'url': 'magnet:?xt=urn:btih:24D09E3684A2180BB2E55FCBE496DC247066047E&dn=stranger+things+s01e07+webrip+x264+turbo+ettv&tr=udp%3A%2F%2Ftracker.publicbt.com%2Fannounce&tr=udp%3A%2F%2Fglotorrents.pw%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A80%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce'}, '480p': {'provider': 'ettv', 'peers': 1081, 'seeds': 550, 'url': 'magnet:?xt=urn:btih:24D09E3684A2180BB2E55FCBE496DC247066047E&dn=stranger+things+s01e07+webrip+x264+turbo+ettv&tr=udp%3A%2F%2Ftracker.publicbt.com%2Fannounce&tr=udp%3A%2F%2Fglotorrents.pw%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A80%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce'}}, 'watched': {'watched': False}, 'first_aired': 1468566000, 'date_based': False, 'overview': 'Eleven struggles to reach Will, while Lucas warns that "the bad men are coming." Nancy and Jonathan show the police what Jonathan caught on camera.', 'title': 'Chapter Seven: The Bathtub', 'episode': 7, 'season': 1, 'tvdb_id': 5621931}, {'torrents': {'0': {'provider': 'ettv', 'peers': 978, 'seeds': 482, 'url': 'magnet:?xt=urn:btih:BA7642C2A996CC2ABB9AF5226DEC697AEA25A663&dn=stranger+things+s01e08+webrip+x264+turbo+ettv&tr=udp%3A%2F%2Ftracker.publicbt.com%2Fannounce&tr=udp%3A%2F%2Fglotorrents.pw%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A80%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce'}, '480p': {'provider': 'ettv', 'peers': 978, 'seeds': 482, 'url': 'magnet:?xt=urn:btih:BA7642C2A996CC2ABB9AF5226DEC697AEA25A663&dn=stranger+things+s01e08+webrip+x264+turbo+ettv&tr=udp%3A%2F%2Ftracker.publicbt.com%2Fannounce&tr=udp%3A%2F%2Fglotorrents.pw%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A80%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce'}}, 'watched': {'watched': False}, 'first_aired': 1468566000, 'date_based': False, 'overview': "Dr. Brenner holds Hopper and Joyce for questioning while the boys wait with Eleven in the gym. Back at Will's, Nancy and Jonathan prepare for battle.", 'title': 'Chapter Eight: The Upside Down', 'episode': 8, 'season': 1, 'tvdb_id': 5621932}, {'torrents': {'0': {'provider': 'EZTV', 'peers': 0, 'seeds': 0, 'url': 'magnet:?xt=urn:btih:eb00500ca7b10651a7149aca862c56ff15bafdef&dn=Stranger.Things.S02E01.WEBRip.x264-RARBG%5Beztv%5D.mp4%5Beztv%5D&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A80&tr=udp%3A%2F%2Fglotorrents.pw%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Fexodus.desync.com%3A6969'}, '480p': {'provider': 'EZTV', 'peers': 0, 'seeds': 0, 'url': 'magnet:?xt=urn:btih:eb00500ca7b10651a7149aca862c56ff15bafdef&dn=Stranger.Things.S02E01.WEBRip.x264-RARBG%5Beztv%5D.mp4%5Beztv%5D&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A80&tr=udp%3A%2F%2Fglotorrents.pw%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Fexodus.desync.com%3A6969'}, '720p': {'provider': 'EZTV', 'peers': 0, 'seeds': 0, 'url': 'magnet:?xt=urn:btih:30b0fa36086c4401630535a3a5f0c75902ca8f21&dn=Stranger.Things.S02E01.Chapter.One.MADMAX.720p.NF.WEBRip.DD5.1.x264-NTb%5Beztv%5D.mkv%5Beztv%5D&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A80&tr=udp%3A%2F%2Fglotorrents.pw%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Fexodus.desync.com%3A6969'}}, 'watched': {'watched': False}, 'first_aired': 1509087600, 'date_based': False, 'overview': 'As the town preps for Halloween, a high-scoring rival shakes things up at the arcade, and a skeptical Hopper inspects a field of rotting pumpkins.', 'title': 'Chapter One: MADMAX', 'episode': 1, 'season': 2, 'tvdb_id': 5734306}, {'torrents': {'0': {'provider': 'EZTV', 'peers': 0, 'seeds': 0, 'url': 'magnet:?xt=urn:btih:f24ef43ddc6f01c3c111eb79710b5a6a3ff3f6ff&dn=Stranger.Things.S02E02.WEBRip.x264-RARBG%5Beztv%5D.mp4%5Beztv%5D&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A80&tr=udp%3A%2F%2Fglotorrents.pw%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Fexodus.desync.com%3A6969'}, '480p': {'provider': 'EZTV', 'peers': 0, 'seeds': 0, 'url': 'magnet:?xt=urn:btih:f24ef43ddc6f01c3c111eb79710b5a6a3ff3f6ff&dn=Stranger.Things.S02E02.WEBRip.x264-RARBG%5Beztv%5D.mp4%5Beztv%5D&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A80&tr=udp%3A%2F%2Fglotorrents.pw%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Fexodus.desync.com%3A6969'}, '720p': {'provider': 'EZTV', 'peers': 0, 'seeds': 0, 'url': 'magnet:?xt=urn:btih:41622c5b7ef820dcbea2d3e97bb1e8eaf7bbb96c&dn=Stranger.Things.S02E02.Chapter.Two.Trick.Or.Treat.Freak.720p.NF.WEBRip.DD5.1.x264-NTb%5Beztv%5D.mkv%5Beztv%5D&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A80&tr=udp%3A%2F%2Fglotorrents.pw%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Fexodus.desync.com%3A6969'}}, 'watched': {'watched': False}, 'first_aired': 1509087600, 'date_based': False, 'overview': "After Will sees something terrible on trick-or-treat night, Mike wonders whether Eleven's still out there. Nancy wrestles with the truth about Barb.", 'title': 'Chapter Two: Trick or Treat, Freak', 'episode': 2, 'season': 2, 'tvdb_id': 5734307}, {'torrents': {'0': {'provider': 'EZTV', 'peers': 0, 'seeds': 0, 'url': 'magnet:?xt=urn:btih:f59c9e1d4e9d429380d241af7192a2855546af8b&dn=Stranger.Things.S02E03.WEBRip.x264-RARBG%5Beztv%5D.mp4%5Beztv%5D&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A80&tr=udp%3A%2F%2Fglotorrents.pw%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Fexodus.desync.com%3A6969'}, '480p': {'provider': 'EZTV', 'peers': 0, 'seeds': 0, 'url': 'magnet:?xt=urn:btih:f59c9e1d4e9d429380d241af7192a2855546af8b&dn=Stranger.Things.S02E03.WEBRip.x264-RARBG%5Beztv%5D.mp4%5Beztv%5D&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A80&tr=udp%3A%2F%2Fglotorrents.pw%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Fexodus.desync.com%3A6969'}, '720p': {'provider': 'EZTV', 'peers': 0, 'seeds': 0, 'url': 'magnet:?xt=urn:btih:94f9c50aa009e4a283975bec06d0405fc73d19ad&dn=Stranger.Things.S02E03.Chapter.Three.The.Pollywog.720p.NF.WEBRip.DD5.1.x264-NTb%5Beztv%5D.mkv%5Beztv%5D&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A80&tr=udp%3A%2F%2Fglotorrents.pw%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Fexodus.desync.com%3A6969'}}, 'watched': {'watched': False}, 'first_aired': 1509087600, 'date_based': False, 'overview': 'Dustin adopts a strange new pet, and Eleven grows increasingly impatient. A well-meaning Bob urges Will to stand up to his fears.', 'title': 'Chapter Three: The Pollywog', 'episode': 3, 'season': 2, 'tvdb_id': 5734308}, {'torrents': {'0': {'provider': 'EZTV', 'peers': 0, 'seeds': 0, 'url': 'magnet:?xt=urn:btih:7f888e374e4ec52f469c03363b87e05d8898294f&dn=Stranger.Things.S02E04.WEBRip.x264-RARBG%5Beztv%5D.mp4%5Beztv%5D&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A80&tr=udp%3A%2F%2Fglotorrents.pw%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Fexodus.desync.com%3A6969'}, '480p': {'provider': 'EZTV', 'peers': 0, 'seeds': 0, 'url': 'magnet:?xt=urn:btih:7f888e374e4ec52f469c03363b87e05d8898294f&dn=Stranger.Things.S02E04.WEBRip.x264-RARBG%5Beztv%5D.mp4%5Beztv%5D&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A80&tr=udp%3A%2F%2Fglotorrents.pw%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Fexodus.desync.com%3A6969'}, '720p': {'provider': 'EZTV', 'peers': 0, 'seeds': 0, 'url': 'magnet:?xt=urn:btih:81fcf5926d1aafb59316d626bf678346626fbd64&dn=Stranger.Things.S02E04.Chapter.Four.Will.The.Wise.720p.NF.WEBRip.DD5.1.x264-NTb%5Beztv%5D.mkv%5Beztv%5D&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A80&tr=udp%3A%2F%2Fglotorrents.pw%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Fexodus.desync.com%3A6969'}}, 'watched': {'watched': False}, 'first_aired': 1509087600, 'date_based': False, 'overview': 'An ailing Will opens up to Joyce -- with disturbing results. While Hopper digs for the truth, Eleven unearths a surprising discovery.', 'title': 'Chapter Four: Will the Wise', 'episode': 4, 'season': 2, 'tvdb_id': 5734309}, {'torrents': {'0': {'provider': 'EZTV', 'peers': 0, 'seeds': 0, 'url': 'magnet:?xt=urn:btih:a6b6ad08309221e491aad46856c69eac05d244c7&dn=Stranger.Things.S02E05.WEBRip.x264-RARBG%5Beztv%5D.mp4%5Beztv%5D&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A80&tr=udp%3A%2F%2Fglotorrents.pw%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Fexodus.desync.com%3A6969'}, '480p': {'provider': 'EZTV', 'peers': 0, 'seeds': 0, 'url': 'magnet:?xt=urn:btih:a6b6ad08309221e491aad46856c69eac05d244c7&dn=Stranger.Things.S02E05.WEBRip.x264-RARBG%5Beztv%5D.mp4%5Beztv%5D&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A80&tr=udp%3A%2F%2Fglotorrents.pw%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Fexodus.desync.com%3A6969'}, '720p': {'provider': 'EZTV', 'peers': 0, 'seeds': 0, 'url': 'magnet:?xt=urn:btih:e71c28ad6cca934221146637981f48288baec750&dn=Stranger.Things.S02E05.Chapter.Five.Dig.Dug.720p.NF.WEBRip.DD5.1.x264-NTb%5Beztv%5D.mkv%5Beztv%5D&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A80&tr=udp%3A%2F%2Fglotorrents.pw%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Fexodus.desync.com%3A6969'}}, 'watched': {'watched': False}, 'first_aired': 1509087600, 'date_based': False, 'overview': 'Nancy and Jonathan swap conspiracy theories with a new ally as Eleven searches for someone from her past. “Bob the Brain” tackles a difficult problem.', 'title': 'Chapter Five: Dig Dug', 'episode': 5, 'season': 2, 'tvdb_id': 5734310}, {'torrents': {'0': {'provider': 'EZTV', 'peers': 0, 'seeds': 0, 'url': 'magnet:?xt=urn:btih:8951b540d3b49c1878792d44a3c42d40ee56f6d6&dn=Stranger.Things.S02E06.WEBRip.x264-RARBG%5Beztv%5D.mp4%5Beztv%5D&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A80&tr=udp%3A%2F%2Fglotorrents.pw%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Fexodus.desync.com%3A6969'}, '480p': {'provider': 'EZTV', 'peers': 0, 'seeds': 0, 'url': 'magnet:?xt=urn:btih:8951b540d3b49c1878792d44a3c42d40ee56f6d6&dn=Stranger.Things.S02E06.WEBRip.x264-RARBG%5Beztv%5D.mp4%5Beztv%5D&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A80&tr=udp%3A%2F%2Fglotorrents.pw%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Fexodus.desync.com%3A6969'}, '720p': {'provider': 'EZTV', 'peers': 0, 'seeds': 0, 'url': 'magnet:?xt=urn:btih:7f7d7ec2c64434e6be352ffb5ae15f48c7fe517f&dn=Stranger.Things.S02E06.Chapter.Six.The.Spy.720p.NF.WEBRip.DD5.1.x264-NTb%5Beztv%5D.mkv%5Beztv%5D&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A80&tr=udp%3A%2F%2Fglotorrents.pw%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Fexodus.desync.com%3A6969'}}, 'watched': {'watched': False}, 'first_aired': 1509087600, 'date_based': False, 'overview': "Will's connection to a shadowy evil grows stronger, but no one's quite sure how to stop it. Elsewhere, Dustin and Steve forge an unlikely bond.", 'title': 'Chapter Six: The Spy', 'episode': 6, 'season': 2, 'tvdb_id': 5734311}, {'torrents': {'0': {'provider': 'EZTV', 'peers': 0, 'seeds': 0, 'url': 'magnet:?xt=urn:btih:8023824938b68bee58d43dfd58d36d341e833472&dn=Stranger.Things.S02E07.WEBRip.x264-RARBG%5Beztv%5D.mp4%5Beztv%5D&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A80&tr=udp%3A%2F%2Fglotorrents.pw%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Fexodus.desync.com%3A6969'}, '480p': {'provider': 'EZTV', 'peers': 0, 'seeds': 0, 'url': 'magnet:?xt=urn:btih:8023824938b68bee58d43dfd58d36d341e833472&dn=Stranger.Things.S02E07.WEBRip.x264-RARBG%5Beztv%5D.mp4%5Beztv%5D&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A80&tr=udp%3A%2F%2Fglotorrents.pw%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Fexodus.desync.com%3A6969'}, '720p': {'provider': 'EZTV', 'peers': 0, 'seeds': 0, 'url': 'magnet:?xt=urn:btih:d8194aac804fcf7a13287ae583a7b7c9ee802c4b&dn=Stranger.Things.S02E07.Chapter.Seven.The.Lost.Sister.720p.REPACK.NF.WEBRip.DD5.1.x264-NTb%5Beztv%5D.mkv%5Beztv%5D&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A80&tr=udp%3A%2F%2Fglotorrents.pw%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Fexodus.desync.com%3A6969'}}, 'watched': {'watched': False}, 'first_aired': 1509087600, 'date_based': False, 'overview': 'Psychic visions draw Eleven to a band of violent outcasts and an angry girl with a shadowy past.', 'title': 'Chapter Seven: The Lost Sister', 'episode': 7, 'season': 2, 'tvdb_id': 5734312}, {'torrents': {'0': {'provider': 'EZTV', 'peers': 0, 'seeds': 0, 'url': 'magnet:?xt=urn:btih:1e3bd2ddcde0567b5b8d4a5e5cb799c786b9d4ce&dn=Stranger.Things.S02E08.WEBRip.x264-RARBG%5Beztv%5D.mp4%5Beztv%5D&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A80&tr=udp%3A%2F%2Fglotorrents.pw%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Fexodus.desync.com%3A6969'}, '480p': {'provider': 'EZTV', 'peers': 0, 'seeds': 0, 'url': 'magnet:?xt=urn:btih:1e3bd2ddcde0567b5b8d4a5e5cb799c786b9d4ce&dn=Stranger.Things.S02E08.WEBRip.x264-RARBG%5Beztv%5D.mp4%5Beztv%5D&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A80&tr=udp%3A%2F%2Fglotorrents.pw%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Fexodus.desync.com%3A6969'}, '720p': {'provider': 'EZTV', 'peers': 0, 'seeds': 0, 'url': 'magnet:?xt=urn:btih:2c0c52f081f00614c64ee6bb095c44caeaa1ef05&dn=Stranger.Things.S02E08.Chapter.Eight.The.Mind.Flayer.720p.NF.WEBRip.DD5.1.x264-NTb%5Beztv%5D.mkv%5Beztv%5D&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A80&tr=udp%3A%2F%2Fglotorrents.pw%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Fexodus.desync.com%3A6969'}}, 'watched': {'watched': False}, 'first_aired': 1509087600, 'date_based': False, 'overview': 'An unlikely hero steps forward when a deadly development puts the Hawkins Lab on lockdown, trapping Will and several others inside.', 'title': 'Chapter Eight: The Mind Flayer', 'episode': 8, 'season': 2, 'tvdb_id': 5734313}, {'torrents': {'0': {'provider': 'EZTV', 'peers': 0, 'seeds': 0, 'url': 'magnet:?xt=urn:btih:f71c26f1ae2776d81707180632ed1509ddb7f9cc&dn=Stranger.Things.S02E09.WEBRip.x264-RARBG%5Beztv%5D.mp4%5Beztv%5D&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A80&tr=udp%3A%2F%2Fglotorrents.pw%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Fexodus.desync.com%3A6969'}, '480p': {'provider': 'EZTV', 'peers': 0, 'seeds': 0, 'url': 'magnet:?xt=urn:btih:f71c26f1ae2776d81707180632ed1509ddb7f9cc&dn=Stranger.Things.S02E09.WEBRip.x264-RARBG%5Beztv%5D.mp4%5Beztv%5D&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A80&tr=udp%3A%2F%2Fglotorrents.pw%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Fexodus.desync.com%3A6969'}, '720p': {'provider': 'EZTV', 'peers': 0, 'seeds': 0, 'url': 'magnet:?xt=urn:btih:5ede1d5c7250ef1a16f239021e24bd7cba1a10aa&dn=Stranger.Things.S02E09.Chapter.Nine.The.Gate.720p.NF.WEBRip.DD5.1.x264-NTb%5Beztv%5D.mkv%5Beztv%5D&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A80&tr=udp%3A%2F%2Fglotorrents.pw%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Fexodus.desync.com%3A6969'}}, 'watched': {'watched': False}, 'first_aired': 1509087600, 'date_based': False, 'overview': "Eleven makes plans to finish what she started while the survivors turn up the heat on the monstrous force that's holding Will hostage.", 'title': 'Chapter Nine: The Gate', 'episode': 9, 'season': 2, 'tvdb_id': 5734314}], 'genres': ['drama', 'fantasy', 'science-fiction', 'mystery', 'adventure', 'horror'], 'images': {'poster': 'http://image.tmdb.org/t/p/w500/esKFbCWAGyUUNshT5HE5BIpvbcL.jpg', 'fanart': 'http://image.tmdb.org/t/p/w500/56v2KjBlU4XaOv9rVYEQypROD7P.jpg', 'banner': 'http://image.tmdb.org/t/p/w500/esKFbCWAGyUUNshT5HE5BIpvbcL.jpg'}, 'rating': {'percentage': 88, 'watching': 458, 'votes': 23353, 'loved': 100, 'hated': 100}}


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

    self.manager.remove_widget(self)