#!/usr/bin/env python
# coding: utf-8


from kivy.lang import Builder
from kivy.uix.screenmanager import Screen


from menu import BottomMenu



class Signup(Screen):
    def rgb(self, r, g, b, alpha=1):
        return BottomMenu.rgb(self, r, g, b, alpha)
        
    def valid_credentials(self, email_textinput, pw_textinput, pw_confirm_textinput):
        email = email_textinput.text
        pw = pw_textinput.text
        pw_confirm = pw_confirm_textinput.text
        
        
        
        
        if pw != pw_confirm:
            return False
            
        if email == '' or pw == '' or pw_confirm == '':
            return False
        if email.find('@') == -1:
            return False
            
            

            
            

            

        #ToDo: DB storing
        #ToDo: depending on the error...store it into self.ids.errorlbl.text
        return True
        
    def on_pre_leave(self, *args):
        self.manager.transition.direction = 'down'
        
        
        

kv = Builder.load_file('signup.kv')
