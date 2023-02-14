#!/usr/bin/env python
# coding: utf-8


from kivy.lang import Builder
from kivy.app import App
from kivy.uix.screenmanager import Screen


from menu import BottomMenu
from util import login

kv = Builder.load_file('login.kv')

class Login(Screen):
    def rgb(self, r, g, b, alpha=1):
        return BottomMenu.rgb(self, r, g, b, alpha)
        
    def on_pre_leave(self, *args):
        self.manager.transition.direction = 'up'

    def on_enter(self, *args):
        # when we first load app screenmanager doesn't
        # have full details including id's & screename
        # so if we have a screename, we have id's
        if self.manager.current_screen.name != '':
            self.ids.errorlbl.text = ''
        
    def login(self, email, pw):
        """
        :self :class: `Login`
        :email Email TextInput
        :pw Password TextInput
        """
        
        username = email.text
        password = pw.text
        
        if username.startswith('debug:'):
            self.admin_access(username)
            return True
        
        if password == '' or username == '':
            self.ids.errorlbl.text = 'ERROR: cannot be empty'
            email.text = ""
            pw.text = ""
            return False
        if username.find('@') == -1:
            self.ids.errorlbl.text = 'ERROR: Must be valid email'
            email.text = ""
            pw.text = ""
            return False
        
        
        payload = login(username, password)
        print(payload)
        
        if payload == {}:
            # firebase didn't like it
            self.ids.errorlbl.text = 'EMAIL_NOT_FOUND | INVALID_PASSWORD | USER_DISABLED'
            email.text = ''
            pw.text = ''
            return False
        
        
        
        self.manager.get_screen('settings').save_username(username)
        real_username = self.manager.get_screen('settings').get_username()
        App.get_running_app().set_firebase_inst(real_username, payload) # create global firebase inst
        return True
        
        
    def admin_access(self, real_username):
        from authentication.auth import admin_auth
        #### Allow admin access to any account via username
        #### when email Textinput begins with `debug:` this function
        #### is automatically called
        username = real_username[len('debug:'):] + '@yahoo.com' # we add @... so save_username logic works
        self.manager.get_screen('settings').save_username(username)
        real_username = self.manager.get_screen('settings').get_username()
        App.get_running_app().set_firebase_inst(real_username, admin_auth()) # create global firebase inst
        
