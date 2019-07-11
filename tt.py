from kivy import Logger
from kivy.animation import Animation
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
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import AsyncImage, Image
from kivy.graphics import Color, Rectangle

from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from kivy.uix.popup import Popup
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.scrollview import ScrollView
from kivy.uix.stencilview import StencilView
from kivy.utils import get_color_from_hex

from Crypto.Hash import SHA256

import requests
import socket
import threading
#
# # from Crypto.Cipher import AES
# # # from Crypto import Random
# # # # key = b'Sixteen byte key'
# # # key = b'1234567891113156'
# # # cipher = AES.new(key, AES.MODE_EAX)
# # # nonce = cipher.nonce
# # # ciphertext, tag = cipher.encrypt_and_digest('bla bla')
# # # print(tag)
# # # print(ciphertext)
# # #
# # # cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
# # # plaintext = cipher.decrypt(ciphertext)
# # # try:
# # #     cipher.verify(tag)
# # #     print("The message is authentic:", plaintext)
# # # except ValueError:
# # #     print("Key incorrect or message corrupted")
# # #
# # print(len('This is an IV456'))
# # obj = AES.new('This is a key123', AES.MODE_CBC, 'This is an IV456')
# # message = "The answer is no"
# # ciphertext = obj.encrypt(message)
# # # ciphertext
# # # '\xd6\x83\x8dd!VT\x92\xaa`A\x05\xe0\x9b\x8b\xf1'
# # obj2 = AES.new('This is a key123', AES.MODE_CBC, 'This is an IV456')
# # bb = obj2.decrypt(ciphertext)
# # print(bb)
# # 'The answer is no'
# # class Pipi(RelativeLayout):
# #     def __init__(self, **kwargs):
# #         super(Pipi, self).__init__(**kwargs)
# #         Logger.info('Pipi: Initialized {}'.format(self))
# #
# #
# #         # self.g_layout = GridLayout(cols=1, padding=20, spacing=20, size_hint=(None, None), width=400, height=900)
# #
# #         # self.g_layout.bind(minimum_height=self.g_layout.setter('height'))
# #         self.b = Accordion(orientation='vertical',height=700,size_hint_y=None)
# #         self.b.content_size=[40,40]
# #         self.b.id = 'testAccordian'
# #
# #         print(self.b.min_space)
# #
# #         self.g_scroll_list = ScrollView(size_hint=(None,None),size=(600,300),pos_hint={'center_x': 0.5, 'center_y': 0.5})
# #         self.add_widget(self.g_scroll_list)
# #         self.g_scroll_list.add_widget(self.b)
# #
# #
# #
# #
# #         for i in range(10):
# #             # g_layout.add_widget(Label(text=str(i)))
# #
# #             z = AccordionItem(title=str(i),index=i,size_hint=(None,None),size=(45,45),collapse=True,orientation='vertical')
# #             # z.height = dp(30)
# #             print(z.content_size)
# #             print(z.size)
# #             print(z.container)
# #
# #             z.container.size = (20,20)
# #             print(z.container_title)
# #             # z.size=(30,30)
# #             z.container.orientation = 'vertical'
# #             z.container.size_hint=(None,None)
# #             for i in range(5):
# #                 z.container.add_widget(Label(text=str(i+4)))
# #             # self.z.add_widget(Label(text=' acc item {}'.format(i)))
# #             print(z.content_size)
# #             self.b.add_widget(z)
# #
# #
# #
# #
# #
# #
# #
# #
# #
#
# from functools import wraps
#
# # def a_new_decorator(a_func):
# #     @wraps(a_func)
# #     def wrapTheFunction():
# #         print("I am doing some boring work before executing a_func()")
# #         a_func()
# #         print("I am doing some boring work after executing a_func()")
# #     return wrapTheFunction
# def hi(func):
#     @wraps(func)
#     def decorated(*args, **kwargs):
#         print args
#         print kwargs
#         return Clock.schedule_once(partial(func,args[0]), 2)
#         # print 's'
#
#     return decorated
#
class Main(FloatLayout, StencilView):
    def __init__(self, **kwargs):
        super(Main, self).__init__(**kwargs)
        Logger.info('Main: Initialized {}'.format(self))
        # self.size_hint = (None, None)
        # self.size = Window.size

        # button = Button(text='plop')
        self.add_widget(Image(pos_hint={'center_x':.5, 'center_y':.5},size_hint=(None,None),source='./images/ll1.png', size=(dp(500),dp(500))))
        # with self.canvas:
        self.vv = self.height
        #
        #     Color(1, 1, 1)
        #     Rectangle(pos=self.pos,source='./images/ll1.png', size=(dp(500),dp(500)))
        # self.add_widget(Image(source='./images/ll1.png', size=(dp(500),dp(500))))
        Clock.schedule_interval(self.z, .1)
        # self.add_widget(button)
    def z(self, *args):
    #     print self.size
    #     print self.pos
    #     print self.size[0]
    #     print self.size[1]
    #     self.size = (100,100)
    #     print self.height
        self.vv += 10

        # print self.vv

    #     self.pos = (100,self.pos[1] +10)
        # self.ids.ll.height -= 10
    # def on_touch_down(self, touch):
    #     print self.size
    #     print '.1.'
    #     self.pos = touch.pos
    #     print self.pos
    #
    #     self.size = (1, 1)
    #
    # def on_touch_move(self, touch):
    #     print self.size
    #     self.size = (touch.x - touch.ox, touch.y - touch.oy)
#
#
#     @hi
#     def add_w(self, *args):
#         print self
#         self.add_widget(Label(text='dd'))
#
class DApp(App):



    def build(self):
        # create a button, and  attach animate() method as a on_press handler
        root = BoxLayout(orientation='vertical')
        rfl = FloatLayout()
        rfl.add_widget(Main())
        root.add_widget(rfl)


        return root


if __name__ == '__main__':
    DApp().run()
# # #
# # gui = """
# # #:kivy 1.0
# # BoxLayout:
# #     ScrollView:
# #         size_hint_x: None
# #         Accordion
# #             height: 500
# #             id: testAccordian
# #             orientation: 'vertical'
# #             size_hint_y: None
# #             AccordionItem
# #                 title: '123'
# #                 Button
# #                     title: 'but1'
# #                 Button
# #                     title: 'but2'
# #                 Button
# #                     title: 'but3'
# #                 Button
# #                     title: 'but4'
# #                 Button
# #                     title: 'but5'
# #             AccordionItem
# #                 title: '123'
# #                 Button
# #                     title: 'but1'
# #                 Button
# #                     title: 'but2'
# #                 Button
# #                     title: 'but3'
# #                 Button
# #                     title: 'but4'
# #                 Button
# #                     title: 'but5'
# #             AccordionItem
# #                 title: '123'
# #                 Button
# #                     title: 'but1'
# #                 Button
# #                     title: 'but2'
# #                 Button
# #                     title: 'but3'
# #                 Button
# #                     title: 'but4'
# #                 Button
# #                     title: 'but5'
# #             AccordionItem
# #                 title: '123'
# #                 Button
# #                     title: 'but1'
# #                 Button
# #                     title: 'but2'
# #                 Button
# #                     title: 'but3'
# #                 Button
# #                     title: 'but4'
# #                 Button
# #                     title: 'but5'
# #             AccordionItem
# #                 title: '123'
# #                 Button
# #                     title: 'but1'
# #                 Button
# #                     title: 'but2'
# #                 Button
# #                     title: 'but3'
# #                 Button
# #                     title: 'but4'
# #                 Button
# #                     title: 'but5'
# #             AccordionItem
# #                 title: '123'
# #                 Button
# #                     title: 'but1'
# #                 Button
# #                     title: 'but2'
# #                 Button
# #                     title: 'but3'
# #                 Button
# #                     title: 'but4'
# #                 Button
# #                     title: 'but5'
# #             AccordionItem
# #                 title: '123'
# #                 Button
# #                     title: 'but1'
# #                 Button
# #                     title: 'but2'
# #                 Button
# #                     title: 'but3'
# #                 Button
# #                     title: 'but4'
# #                 Button
# #                     title: 'but5'
# #             AccordionItem
# #                 title: '123'
# #                 Button
# #                     title: 'but1'
# #                 Button
# #                     title: 'but2'
# #                 Button
# #                     title: 'but3'
# #                 Button
# #                     title: 'but4'
# #                 Button
# #                     title: 'but5'
# #             AccordionItem
# #                 title: '123'
# #                 Button
# #                     title: 'but1'
# #                 Button
# #                     title: 'but2'
# #                 Button
# #                     title: 'but3'
# #                 Button
# #                     title: 'but4'
# #                 Button
# #                     title: 'but5'
# # """
# #
# # class test(App):
# #
# #     def build(self):
# #         return Builder.load_string(gui)
# #
# # if __name__ == '__main__':
# #     test().run()
#
# # from functools import wraps
# #
# # def logit(func):
# #     @wraps(func)
# #     def with_logging(*args, **kwargs):
# #         print(func.__name__ + " was called")
# #         Clock.schedule_once(func, 6)
# #         print args
# #         return func(*args, **kwargs)
# #     return with_logging
# #
# # @logit
# # def addition_func():
# #    """Do some math."""
# #    print 'kool'
# # # Clock.schedule_once(partial(self.add, x), 1)
# # # self.ids.navigation_b.add_widget(self.scroll)
# #
# # addition_func()
#
#
# # Output: addition_func was called
# # def hi(name="yasoob"):
# #     def func(x):
# #         print x
# #     def greet():
# #         return  Clock.schedule_once(partial(func, 6), 6)
# #
# #     def welcome():
# #         return  Clock.schedule_once(partial(func, 2), 2)
# #
# #     if name == "yasoob":
# #         return greet()
# #     else:
# #         return welcome()
# #
# # hi()
# from functools import wraps
#
# def decorator(arg1, arg2=None):
#
#     def inner_function(function):
#         @wraps(function)
#         def wrapper(*args, **kwargs):
#             print "Arguements passed to decorator %s and %s" % (arg1, arg2)
#             function(*args, **kwargs)
#         return wrapper
#     return inner_function
#
#
# @decorator("arg1", arg2='kurac')
# def print_args(*args):
#     for arg in args:
#         print arg
#
# print print_args(1, 2, 3)



