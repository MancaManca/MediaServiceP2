from kivy import Logger
from kivy.storage.jsonstore import JsonStore

media_keys = ['hashed_dic_shows', 'hashed_dic_show', 'hashed_dic_movie', 'hashed_dic_movies', 'hashed_dic_search']
filter_keys = ['order', 'type', 'genre', 'sort']


class DB(object):
    """Base DB class"""

    def __init__(self, file_name, keys_list, name):
        self.name = name
        self.file_name = file_name
        self.db = JsonStore(self.file_name)
        self.keys = keys_list
        Logger.info('{}: Initialized DB'.format(self.name))
        Logger.info('{} DB: file name {} , keys {}'.format(self.name, file_name, keys_list))
        self._create()

    def _create(self):

        for key in self.keys:
            if self.db.exists(key):
                Logger.warning('{} DB: Key Exists {}'.format(self.name, key))
                # Logger.warning('Existsing keys {}'.format(self.db[key]))

            else:
                self.db.put(key, val='')

                Logger.warning('{} DB: Key Does not exist Adding {}'.format(self.name, key))
        pass

    def _update(self):
        pass

    def _put(self, key=None, val=None, val_second=None):
        try:
            if val_second:
                self.db.put(key, val=val, val_second=val_second)
                Logger.info('{} DB : Adding key {} with addition'.format(self.name, key))
            else:
                self.db.put(key, val=val)
                Logger.info('{} DB: Adding key {}'.format(self.name, key))

        except Exception as e:
            Logger.error('{} DB : Failed to add key {} due to {}'.format(self.name, key, e))
            pass

    def _delete(self, key=None):
        try:
            self.db.delete(key)
            Logger.info('{} DB : Deleting key {} '.format(self.name, key))

        except Exception as e:
            Logger.error('{} DB: Failed to delete key {} due to {}'.format(self.name, key, e))
            pass
        pass

    def _get(self, key=None, child_key=None):
        if self.db.exists(key):
            if child_key:
                return self.db[key][child_key]
            return self.db[key]['val']
        else:
            Logger.error('{} DB: Key {} does not exist'.format(self.name, key))
            return False
        pass

    def _get_keys(self):
        try:
            Logger.info('{} DB: Getting keys'.format(self.name))
            return self.db.keys()

        except Exception as e:
            Logger.error('{} DB: Getting keys failed due to {}'.format(self.name, e))
            pass
        pass

    def _exists(self, key):
        if self.db.exists(key):
            Logger.info('{} DB: Key {} exists'.format(self.name, key))
            return True

        Logger.info('{}DB : Key {} does not exist'.format(self.name, key))
        return False


class Media(DB):
    def __init__(self):
        DB.__init__(self, 'media_database.json', media_keys, self.__class__.__name__)

        pass


class Filter(DB):
    def __init__(self):
        DB.__init__(self, 'filter_database.json', filter_keys, self.__class__.__name__)

        pass


class Favourites(DB):
    def __init__(self):
        DB.__init__(self, 'favourites.json', [], self.__class__.__name__)

    pass


class Network(DB):
    def __init__(self):
        DB.__init__(self, 'network.json', [], self.__class__.__name__)

    pass
