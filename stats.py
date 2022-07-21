#!/usr/bin/env python
# coding: utf-8


from kivy.lang import Builder
from kivy.uix.screenmanager import Screen


from menu import BottomMenu



class Statistics(Screen):
    def rgb(self, r, g, b, alpha=1):
        return BottomMenu.rgb(self, r, g, b, alpha)
        
    def on_pre_leave(self, *args):
        self.manager.transition.direction = 'down'
        BottomMenu.save_last_screen('statistics')
        

kv = Builder.load_file('statistics.kv')
