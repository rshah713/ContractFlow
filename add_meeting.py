#!/usr/bin/env python
# coding: utf-8

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty, AliasProperty
from kivy.garden.circulardatetimepicker import CircularTimePicker


from menu import BottomMenu
from util import unique_locations, create_meeting
from datepicker import DatePicker
from edit_meeting import EditMeeting

from datetime import date, datetime

kv = Builder.load_file('add_meeting.kv')

class AddMeeting(Screen):

    def __init__(self, **kwargs):
        super(AddMeeting, self).__init__(**kwargs)
        self.next_location = 'None' # filled on_enter w/ firebase
        self.today = date.today().strftime("%B %d") # 'June 24'
        self.location = ''
        self.timergui = TimePicker(self, 'Start time')
        self.date_save_list = []
        self.calendergui = DatePicker(self)
        
    
    def on_enter(self, *kwargs):
        self.manager.transition.direction = 'down'
        self.firebase = App.get_running_app().get_firebase_connection()
        self.next_location = self.get_next_location()
        
        """
        if self.location == '' it means init ran and those r the options we want
        but if it's not, it means customize_screen was called and we shouldn't be generating label value cuz we got a starting value
        """
        if self.location == '':
            self.update_location_label()
        self.update_label(self.ids.loc) # should always be called self.update_loc_lbl()

        
    def rgb(self, r, g, b, alpha=1):
        return BottomMenu.rgb(self, r, g, b, alpha)
        
    def on_leave(self, *args):
        BottomMenu.save_last_screen('add meeting')
        
    def get_next_location(self):
        for place in unique_locations(self.firebase):
            yield place

    def update_location_label(self):
        try:
            self.location = next(self.next_location)
        except StopIteration:
            self.next_location = self.get_next_location()
            self.location =  next(self.next_location)
            
    
    def update_label(self, label):
        """ once the label's VALUE (self.location) has been updated,
        button calls this method to actually update the label to match the field
        """
        label.text = self.location
        
    
            
    def set_timepicker_mode(self, mode):
        """ set the mode of timepicker so we know what label to update """
        """ :mode either 'start time' or 'end time' """
        self.timergui = TimePicker(self, mode)
        

        
    def add_meeting(self, location, date, start, end):
        create_meeting(self.firebase, [start, end, date, location])
        
    def customize_screen(self, location=None, date=None, start=None, finish=None):
        """ used to override defaults on this screen
        prolly called from 'edit meeting' button
        """
        if location is not None:
            self.location = location # special case: since this always being updated on_enter handles this
        if date is not None:
            self.today = date
            self.ids.workdate.text = self.today
        if start is not None:
            self.ids.starttime.text = start
        if finish is not None:
            self.ids.endtime.text = finish

        
class TimePicker(Popup):
    def __init__(self, screen, mode, **kwargs):
        super(TimePicker, self).__init__(**kwargs)
        self.time = None
        self.mode = mode
        self.screen = screen
        
    def set_time(self, res):
        self.time = res
        
    def get_time(self):
        return self.time
        
    def update_label(self):
        print(type(self.time))
        if self.mode == "Start time":
            self.screen.ids.starttime.text = self.time.strftime("%I:%M %p")
        elif self.mode == "End time":
            self.screen.ids.endtime.text = self.time.strftime("%I:%M %p")
            
   
            
    def rgb(self, r, g, b, alpha=1):
        return BottomMenu.rgb(self, r, g, b, alpha)
        
        
