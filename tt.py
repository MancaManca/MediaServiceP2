from kivy import Logger
from kivy.app import App
from kivy.clock import mainthread, Clock
from kivy.core.window import Window
from kivy.lang import Builder
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
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.scrollview import ScrollView
from kivy.utils import get_color_from_hex

from Crypto.Hash import SHA256

import requests
import socket
import threading



class Pipi(RelativeLayout):
    def __init__(self, **kwargs):
        super(Pipi, self).__init__(**kwargs)
        Logger.info('Pipi: Initialized {}'.format(self))


        # self.g_layout = GridLayout(cols=1, padding=20, spacing=20, size_hint=(None, None), width=400, height=900)

        # self.g_layout.bind(minimum_height=self.g_layout.setter('height'))
        self.b = Accordion(orientation='vertical',height=700,size_hint_y=None)
        self.b.content_size=[40,40]
        self.b.id = 'testAccordian'

        print(self.b.min_space)

        self.g_scroll_list = ScrollView(size_hint=(None,None),size=(600,300),pos_hint={'center_x': 0.5, 'center_y': 0.5})
        self.add_widget(self.g_scroll_list)
        self.g_scroll_list.add_widget(self.b)




        for i in range(10):
            # g_layout.add_widget(Label(text=str(i)))

            z = AccordionItem(title=str(i),index=i,size_hint=(None,None),size=(45,45),collapse=True,orientation='vertical')
            # z.height = dp(30)
            print(z.content_size)
            print(z.size)
            print(z.container)

            z.container.size = (20,20)
            print(z.container_title)
            # z.size=(30,30)
            z.container.orientation = 'vertical'
            z.container.size_hint=(None,None)
            for i in range(5):
                z.container.add_widget(Label(text=str(i+4)))
            # self.z.add_widget(Label(text=' acc item {}'.format(i)))
            print(z.content_size)
            self.b.add_widget(z)









class TttApp(App):

    def build(self):
        Logger.info('Application : Initialized {}'.format(self))

        self.root = BoxLayout(orientation='vertical')

        self.root.add_widget(Pipi())

        return self.root



    def quit_app(self, *args):
        self.stop()

    def on_pause(self):
        return True


if __name__ == '__main__':

    TttApp().run()
#
# gui = """
# #:kivy 1.0
# BoxLayout:
#     ScrollView:
#         size_hint_x: None
#         Accordion
#             height: 500
#             id: testAccordian
#             orientation: 'vertical'
#             size_hint_y: None
#             AccordionItem
#                 title: '123'
#                 Button
#                     title: 'but1'
#                 Button
#                     title: 'but2'
#                 Button
#                     title: 'but3'
#                 Button
#                     title: 'but4'
#                 Button
#                     title: 'but5'
#             AccordionItem
#                 title: '123'
#                 Button
#                     title: 'but1'
#                 Button
#                     title: 'but2'
#                 Button
#                     title: 'but3'
#                 Button
#                     title: 'but4'
#                 Button
#                     title: 'but5'
#             AccordionItem
#                 title: '123'
#                 Button
#                     title: 'but1'
#                 Button
#                     title: 'but2'
#                 Button
#                     title: 'but3'
#                 Button
#                     title: 'but4'
#                 Button
#                     title: 'but5'
#             AccordionItem
#                 title: '123'
#                 Button
#                     title: 'but1'
#                 Button
#                     title: 'but2'
#                 Button
#                     title: 'but3'
#                 Button
#                     title: 'but4'
#                 Button
#                     title: 'but5'
#             AccordionItem
#                 title: '123'
#                 Button
#                     title: 'but1'
#                 Button
#                     title: 'but2'
#                 Button
#                     title: 'but3'
#                 Button
#                     title: 'but4'
#                 Button
#                     title: 'but5'
#             AccordionItem
#                 title: '123'
#                 Button
#                     title: 'but1'
#                 Button
#                     title: 'but2'
#                 Button
#                     title: 'but3'
#                 Button
#                     title: 'but4'
#                 Button
#                     title: 'but5'
#             AccordionItem
#                 title: '123'
#                 Button
#                     title: 'but1'
#                 Button
#                     title: 'but2'
#                 Button
#                     title: 'but3'
#                 Button
#                     title: 'but4'
#                 Button
#                     title: 'but5'
#             AccordionItem
#                 title: '123'
#                 Button
#                     title: 'but1'
#                 Button
#                     title: 'but2'
#                 Button
#                     title: 'but3'
#                 Button
#                     title: 'but4'
#                 Button
#                     title: 'but5'
#             AccordionItem
#                 title: '123'
#                 Button
#                     title: 'but1'
#                 Button
#                     title: 'but2'
#                 Button
#                     title: 'but3'
#                 Button
#                     title: 'but4'
#                 Button
#                     title: 'but5'
# """
#
# class test(App):
#
#     def build(self):
#         return Builder.load_string(gui)
#
# if __name__ == '__main__':
#     test().run()