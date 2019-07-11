import requests
from kivy import Logger
from kivy.storage.jsonstore import JsonStore
from requests.auth import HTTPBasicAuth
import xml.etree.cElementTree as ET



class Plex(object):
    """Plex class"""

    def __init__(self):
        self.plex_store = JsonStore('plex_store_config.json')

        self.user_name = None
        self.user_password = None
        self.token = None
        self.local_network_url = ':32400/'
        self.server = None
        self.base_sign_in_url = 'https://plex.tv'

    def get_servers_api(self):
        servers_url = self.base_sign_in_url + '/pms/servers.xml?includeLite=1'
        # self.user_name = 'manca_xtc@hotmail.com'
        # self.user_password = 'N111111M'
        response = requests.get(servers_url, auth=HTTPBasicAuth(self.user_name, self.user_password))
        parsed_xml = ET.fromstring(response.content)

        if response.status_code == 200:
            serv_temp_dict = {}
            for child in parsed_xml.iter('Server'):
                serv_temp_dict[child.attrib['name']] = child.attrib['localAddresses']
                self.store_credentials(self.user_name, self.user_password)
            return serv_temp_dict
        else:
            raise Exception

    def return_servers(self):
        if self.check_stored_server():
            return self.get_stored_server()

        return self.get_servers_api()

    def credentials_handler(self, user_n=None, user_p=None):
        if self.check_stored_credentials():
            self.user_name, self.user_password = self.get_stored_credentials()

        else:
            self.user_name, self.user_password = user_n, user_p

    def get_servers_handler(self, user_n=None, user_p=None):
        self.credentials_handler(user_n, user_p)
        return self.return_servers()

    def _get_token(self, *args):
        Logger.info('get token')
        sign_in_url = self.base_sign_in_url + '/users/sign_in.xml'
        headers = {'X-Plex-Client-Identifier': self.get_stored_server()[0]}
        user_name, user_pass = self.get_stored_credentials()
        # Logger.info('headers {}'.format(headers))
        response = requests.post(sign_in_url, auth=HTTPBasicAuth(user_name, user_pass), headers=headers)
        # Logger.info('get token response {}'.format(response.content))

        parsed_xml = ET.fromstring(response.content)

        if response.status_code == 201:
            tok_temp_dict = {}
            for child in parsed_xml.iter('user'):

                tok_temp_dict['authToken'] = child.attrib['authToken']

                self.store_token(child.attrib['authToken'])
            # Logger.error(tok_temp_dict)
        #     return tok_temp_dict
        # else:
        #     raise Exception
        #     pass

    def store_token(self, _token):
        Logger.info('Plex store token : {}'.format(_token))

        self.plex_store.put('authtoken', token_value=_token)

    def check_stored_credentials(self):
        if self.plex_store.exists('user_name'):
            return True

        return None

    def check_stored_server(self):
        if self.plex_store.exists('server'):
            return True

        return None

    def get_stored_server(self):
        return self.plex_store.get('server')['server_name'], self.plex_store.get('server')['ip_value']

    def store_server(self, server_name, server_ip):
        self.plex_store.put('server', server_name=server_name, ip_value=server_ip)

    def get_stored_credentials(self):
        return self.plex_store.get('user_name')['value'], self.plex_store.get('user_password')['value']

    def store_credentials(self, user_n, user_p):
        if self.check_stored_credentials() is None:
            self.plex_store.put('user_name', value=user_n)
            self.plex_store.put('user_password', value=user_p)

    def remove_plex_config(self):
        li = [i for i in self.plex_store.keys()]
        for i in li:
            self.plex_store.delete(i)