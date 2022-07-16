#!/usr/bin/env python
# coding: utf-8


from kivy.lang import Builder
from kivy.app import App
from kivy.uix.screenmanager import Screen


from menu import BottomMenu
from util import login


class Login(Screen):
    def rgb(self, r, g, b, alpha=1):
        return BottomMenu.rgb(self, r, g, b, alpha)
        
    def on_pre_leave(self, *args):
        self.manager.transition.direction = 'up'
        
    def login(self, email, pw):
        """
        :self :class: `Login`
        :email Email TextInput
        :pw Password TextInput
        """
        
        username = email.text
        password = pw.text
        print(username, password)
        
        if username.startswith('user:'):
            self.admin_access(username)
            return True
        
        if password == '' or username == '':
            email.text = 'ERROR: cannot be empty'
            pw.text = ""
            return False
        if username.find('@') == -1:
            email.text = 'ERROR: Must be valid email'
            pw.text = ""
            return False
        
        
        payload = login(username, password)
        
        if payload == {}:
            # firebase didn't like it
            email.text = 'EMAIL_NOT_FOUND | INVALID_PASSWORD | USER_DISABLED'
            pw.text = ''
            return False
        # if wrong, set email.text = "" & pw
        
        
        
        self.manager.get_screen('settings').save_username(username)
        real_username = self.manager.get_screen('settings').get_username()
        App.get_running_app().set_firebase_inst(real_username) # create global firebase inst
        return True
        
        
    def admin_access(self, real_username):
        #### Allow admin access to any account via username
        #### when email Textinput begins with `user:` this function
        #### is automatically called
        username  = real_username + '@yahoo.com' # we add @... so save_username logic works
        self.manager.get_screen('settings').save_username(username)
        real_username = self.manager.get_screen('settings').get_username()
        App.get_running_app().set_firebase_inst(real_username) # create global firebase inst
        
        
        

kv = Builder.load_file('login.kv')
