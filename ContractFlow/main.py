#!/usr/bin/env python
# coding: utf-8

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.screenmanager import Screen

from dashboard import Dashboard
from add_meeting import AddMeeting
from edit_meeting import EditMeeting
from main_menu import MainMenu
from manage_locations import ManageLocation
from stats import Statistics
from login import Login
from settings import MySettings


class WindowManager(ScreenManager):
    pass
    
    
class ContractFlowApp(App):
    def build(self):
        return
        

ContractFlowApp().run()
