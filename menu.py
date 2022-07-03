#!/usr/bin/env python
# coding: utf-8


from kivy.lang import Builder
from kivy.uix.gridlayout import GridLayout



kv = Builder.load_file('menu.kv')
class BottomMenu(GridLayout):
    
    last_screen = ['dashboard']

    def rgb(self, r, g, b, alpha=1):
        return (r/255, g/255, b/255, alpha)
    
    def save_last_screen(screen):
        """
        last_screen is static shared across all instances
        save_last_screen should be called by all screen's on_leave
        
        used for back button logic
        """
        BottomMenu.last_screen = [screen]
    


        


