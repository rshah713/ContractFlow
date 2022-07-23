#!/usr/bin/env python
# coding: utf-8

from kivy.app import App
from kivy.lang import Builder
from kivy.utils import platform
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.screenmanager import Screen


if platform == "ios":
    "https://github.com/kivy-garden/garden.mapview/issues/7"
    from os.path import join, dirname
    import kivy.garden
    kivy.garden.garden_app_dir = join(dirname(__file__), "libs", "garden")
    
from dashboard import Dashboard
from add_meeting import AddMeeting
from edit_meeting import EditMeeting
from main_menu import MainMenu
from manage_locations import ManageLocation
from stats import Statistics
from login import Login
from settings import MySettings
from signup import Signup

import ssl

from FirebaseRealtimeDB import Firebase

ssl._create_default_https_context = ssl._create_unverified_context


class WindowManager(ScreenManager):
    pass
    

kv = Builder.load_file('ContractFlow.kv')

class ContractFlowApp(App):
    def build(self):
        return kv
        
    def set_firebase_inst(self, username, credentials):
        self.firebase = Firebase(username, credentials)
    
    def get_firebase_connection(self):
        return self.firebase
        
    
    
ContractFlowApp().run()
