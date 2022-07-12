#!/usr/bin/env python
# coding: utf-8


from kivy.lang import Builder
from kivy.uix.screenmanager import Screen


from menu import BottomMenu


class Login(Screen):
    def rgb(self, r, g, b, alpha=1):
        return BottomMenu.rgb(self, r, g, b, alpha)
        
    def on_pre_leave(self, *args):
        self.manager.transition.direction = 'down'
        
    def login(self, email, pw):
        """
        :self :class: `Login`
        :email Email TextInput
        :pw Password TextInput
        """
        
        username = email.text
        password = pw.text
        print(username, password)
        
        if pw.text == '':
            return False
        
        #ToDo: handle db stuff here
        
        # if wrong, set email.text = "" & pw
        return True
        
        

kv = Builder.load_file('login.kv')
