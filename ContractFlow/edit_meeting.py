#!/usr/bin/env python
# coding: utf-8


from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen

from datetime import date

from menu import BottomMenu
from dashboard import Dashboard
from util import read_data, process_data, delete_entry



kv = Builder.load_file('edit_meeting.kv')
class EditMeeting(Screen):

    def __init__(self, **kwargs):
        super(EditMeeting, self).__init__(**kwargs)
        self.INVALID = True # will be changed in on_enter
        self.selected = ["<start_time>", "<end_time>", "No data to display", "<location>", "No data"] # smthn to keep the __init__ created lables from complaining
        
        
    def on_enter(self, *args):
        self.firebase = App.get_running_app().get_firebase_connection()
        self.entries = self.populate_data()
        self.selected_index = 0
        if len(self.entries) == 0:
            self.INVALID = True # flag to tell screen to hold and stop all buttons from working
            self.selected = ["<start_time>", "<end_time>", "No data to display", "<location>", "No data"]
        else:
            self.INVALID = False
            self.selected = self.entries[self.selected_index] # current selected entry to display
        
    
    def populate_data(self):
        '''
        populate field responsible for all data,
        will be re-populated on a DELETE
        '''
        entries = read_data(self.firebase)
        master_entries = []
        for entry in entries:
            master_entries.append(process_data(entry))
            
        return master_entries
        
        
    def change_screen(self, ind):
        """
        :ind +1 or -1 which will be applied to index
        """
        if self.selected_index + ind < 0:
            self.selected_index += len(self.entries) - 1
        elif self.selected_index + ind >= len(self.entries):
            self.selected_index = 0
        else:
            self.selected_index += ind
            
        self.selected = self.entries[self.selected_index]
        self.update_screen_labels()
        
    def update_screen_labels(self):
        self.ids.date.text = self.selected[2]
        self.ids.location.text = 'Location: {}'.format(self.selected[3])
        self.ids.time.text = '{} - {}'.format(self.selected[0], self.selected[1])
            
    def remove_entry(self):
        delete_entry(self.selected)
        self.entries = self.populate_data()
        self.change_screen(1)

    def rgb(self, r, g, b, alpha=1):
        return BottomMenu.rgb(self, r, g, b, alpha)
        
    def on_pre_leave(self, *args):
        self.manager.transition.direction = 'up'
        BottomMenu.save_last_screen('edit meeting')
