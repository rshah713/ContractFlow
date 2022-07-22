#!/usr/bin/env python
# coding: utf-8

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen


from menu import BottomMenu
from util import all_location_info, get_location_used, delete_meeting, content_present, delete_location


class ManageLocation(Screen):

    """
    most of this page logic has branched from the
    (cleaner) edit_page logic
    """

    def __init__(self, **kwargs):
        super(ManageLocation, self).__init__(**kwargs)
                    # if changing the key here, change next to comment in change_screen
        self.selected = {'Enter new location name': {'address': 'Enter new location address', 'wage': 00.00}} # smthn to keep the __init__ created lables from complaining
        self.temp_key = list(self.selected.keys())[0]
        
        self.INVALID = True # we can't delete the 'enter new location' entry !!!
        
    def on_enter(self, *args):
        
        self.firebase = App.get_running_app().get_firebase_connection()
        self.entries = self.populate_data()
        self.keys = self.populate_data(mode='keys')
        self.selected_index = 0
        self.selected = self.entries[self.keys[self.selected_index]] # this will never fail bc entries will always have 1 elem (default loc)
        self.update_screen()
        if len(self.keys) == 1:
            self.INVALID = True # still can't delete 1 entry
        else:
            self.INVALID = False # ok we got 1 default entry
        
    def populate_data(self, mode=None):
        "populate field responsible for all data"
        location_info = all_location_info(self.firebase)
        if mode == 'keys':
            # since location_info a dict, we cant use index to access
            # we access by keys, so running list of keys is kept which we use index
            # index --> select key --> select entry from dict
            
            return list(location_info.keys())
        return location_info
        
    def change_screen(self, ind):
        """
        :ind +1 or -1 which will be applied to index
        """
        
        if self.selected_index + ind < 0 or self.selected_index + ind >= len(self.keys):
        
            # CHANGE KEY HERE
            # cheap trick -- how to see if we r on enter new page and arrow being pressed
            if self.keys[0] == 'Enter new location name':
                self.entries = self.populate_data()
                self.keys = self.populate_data(mode='keys')
                if len(self.keys) > 1:
                    self.INVALID = False # turn flag off we can
                if ind > 0:
                    # +ind means move to start
                    self.selected_index = 0
                else:
                    self.selected_index = len(self.keys) - 1
            else:
                self.entries = {'Enter new location name': {'address': 'Enter new location address', 'wage': 00.00}} # smthn to keep the __init__ created lables from complaining
                self.keys = list(self.entries.keys())
                self.selected_index = 0
                self.INVALID = True
        else:
            self.selected_index += ind
        
        self.selected = self.entries[self.keys[self.selected_index]]
        self.update_screen()
        
        
    def delete_location(self):
        """
        ContractFlow relies on the fact that any locations in `meetings` can be tied to an address (and wage soon) in `locations`
        so if it tries looking for a deleted location it'll crash
        
        - for this reason, we delete any meetings associated with the deleted location
        # ToDo: revisit this behavior
        """
        locs_used = get_location_used(self.firebase)
        
        appts_to_remove = []
        LOCATION_TO_REMOVE = self.keys[self.selected_index]
        if LOCATION_TO_REMOVE in locs_used.values():
            # if they in here we gotta remove these entries
            for apptNum, loc in locs_used.items():
                if loc == LOCATION_TO_REMOVE:
                    appts_to_remove.append(apptNum)
                    
        delete_meeting(self.firebase, *appts_to_remove)
        
        
        # in the event we may need to shift lastAppt down to latest one
        MEETINGS = self.firebase.read_path('meetings')
        del MEETINGS['lastAppt']
        if MEETINGS == {}: # if empty set to appt0
            self.firebase.patch_path('meetings', {'lastAppt': 'appt0'})
        else: # get keys (appt1, appt2, app3) and use [-1] index
            self.firebase.patch_path('meetings',
                {
                'lastAppt': list(MEETINGS.keys())[-1]
                                     })

        """
        MOST
        IMPORTANT PART
        """
        # ACTUALLY DELETE THE LOCATION
        delete_location(self.firebase, self.keys[self.selected_index])
        
        self.entries = self.populate_data()
        self.keys = self.populate_data(mode='keys')
        self.selected_index = 0
        self.selected = self.entries[self.keys[self.selected_index]] # this will never fail bc entries will always have 1 elem (default loc)
        self.update_screen()
        if len(self.keys) == 1:
            self.INVALID = True

    
        
    def update_screen(self):
        print(self.INVALID)
        self.ids.loc_name.text = self.keys[self.selected_index]
        self.ids.addr.text = self.selected['address']
        self.ids.wage.text = str(self.selected['wage'])
        
    def rgb(self, r, g, b, alpha=1):
        return BottomMenu.rgb(self, r, g, b, alpha)
        
    def on_pre_leave(self, *args):
        self.manager.transition.direction = 'down'
        BottomMenu.save_last_screen('manage location')
        
        
kv = Builder.load_file('manage_location.kv')
