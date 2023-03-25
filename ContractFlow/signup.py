#!/usr/bin/env python
# coding: utf-8


from kivy.lang import Builder
from kivy.uix.screenmanager import Screen


from menu import BottomMenu
from util import signup

kv = Builder.load_file('signup.kv')

class Signup(Screen):

    def __init__(self, **kwargs):
        super(Signup, self).__init__(**kwargs)

    def on_enter(self, *args):
        self.ids.errorlbl.text = ''
    def rgb(self, r, g, b, alpha=1):
        return BottomMenu.rgb(self, r, g, b, alpha)
        
    def valid_credentials(self, email_textinput, pw_textinput, pw_confirm_textinput):
        email = email_textinput.text
        pw = pw_textinput.text
        pw_confirm = pw_confirm_textinput.text
            
        if email == '':
            self.ids.errorlbl.text = "Email cannot be empty"
            return False
        elif pw == '' or pw_confirm == '':
            self.ids.errorlbl.text = "Password cannot be empty"
            return False
        elif pw != pw_confirm:
            self.ids.errorlbl.text = "Passwords must match"
            return False
        if email.find('@') == -1:
            self.ids.errorlbl.text = "Email must be valid"
            return False
            
            
        successful_signup = signup(email, pw)
        
        if not successful_signup: # our checks passed but firebase rejected
            self.ids.errorlbl.text = "EMAIL_EXISTS\nOPERATION_NOT_ALLOWED\nTOO_MANY_ATTEMPTS_TRY_LATER"
            return False
            
        return True
        
        
    def on_pre_leave(self, *args):
        self.manager.transition.direction = 'down'
