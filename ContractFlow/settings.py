#!/usr/bin/env python
# coding: utf-8

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen


from menu import BottomMenu
from datetime import datetime
from util import delete_account



class MySettings(Screen):
    """
    kivy.uix.settings.Settings holds `Settings` namespace
    so when we try to add it to ScreenManager
    it crashes
    """
    
    def __init__(self, **kwargs):
        super(MySettings, self).__init__(**kwargs)
        self.username = ''
        
    def on_enter(self, *args):
        self.firebase = App.get_running_app().get_firebase_connection()
        self.ids.username.text = self.username
        
        
    def rgb(self, r, g, b, alpha=1):
        return BottomMenu.rgb(self, r, g, b, alpha)
        
        
    def save_username(self, email):
        """ called from login screen as a way to save username """
        at_index = email.find('@')
        
        if at_index == -1: # should never hit this bc firebase won't take it
            user = 'ErrorFindingUsername!'
        else:
            user = email[:at_index]
        self.username = user
        
    def get_username(self):
        return self.username
        
    def on_pre_leave(self, *args):
        self.manager.transition.direction = 'down'
        BottomMenu.save_last_screen('settings')
        
    def request_data_deletion(self):
        self.firebase.log_error('AccountDeletion', datetime.now().strftime('%B %d at %I:%M %p'))
        delete_account(self.firebase)
        self.manager.current = 'login'

kv = Builder.load_file('my_settings.kv')
