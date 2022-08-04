#!/usr/bin/env python
# coding: utf-8

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.screenmanager import Screen
from kivy.graphics import Rectangle
from kivy.graphics import Line
from kivy.graphics import Color
from kivy.core.window import Window


from menu import BottomMenu
from util import content_present, num_unique_locations
from util import read_data
from util import create_new_user

from datetime import date



kv = Builder.load_file('dashboard.kv')
class Dashboard(Screen):

    def __init__(self, **kwargs):
        super(Dashboard, self).__init__(**kwargs)
        Window.clearcolor = self.rgb(250, 241, 203)
        
    def on_enter(self, *args):
        self.manager.transition.direction = 'up'
        
        self.firebase = App.get_running_app().get_firebase_connection()
        if self.firebase.read_path('meetings') == {}: # user does not exist?
            create_new_user(self.firebase)
            """
            - IMPORTANT SECURITY NOTE
            
            Possible flaw: if anything goes wrong internally in FirebaseRealtimeDB
            it logs exeption and returns {}
            yet if the directory doesn't exist it also returns {}
                - native urllib returns None but we have if block in
                - Firebase.read_data that turns None into {} when returning
                
            POSSIBLE BUG: something goes wrong, we create_new_user() and wipe data as opposed to only creating new user if they don't exist
            
            ------------
            Possible Fix:
                - in that `if payload == None: payload = {}` (in Fireabse.read_data}
                - change to payload = {'doesNotExist': True}
                - then check here or in util for doesNotExist key vs {} vs actual content
            
            """
            
        self.gen_layout()
        

    def rgb(self, r, g, b, alpha=1):
        return BottomMenu.rgb(self, r, g, b, alpha)
        
    
    def gen_layout(self):
        cnt_present = content_present(self.firebase)
        num_unique_locs = num_unique_locations(self.firebase)
        self.ids.content_present_lbl.text = str(cnt_present)
        self.ids.content_present_lbl.color = self.rgb(13, 59, 102) if cnt_present == 0 else self.rgb(250, 87, 55)
        self.ids.unique_locs_lbl.text = str(num_unique_locs)
        self.ids.unique_locs_lbl.color = self.rgb(13, 59, 102) if num_unique_locs == 0 else self.rgb(250, 87, 55)
        # floatlayout of the remaining 'body' not taken up by menu bars is same for both
        layout = FloatLayout(pos_hint={'center_y':0.5}, size_hint_y= 0.85)
        meeting_count = cnt_present
        if meeting_count == 0:
            # there is no content: switch to no meeting layout
            """
            We need to write GUI via .py file bc
            we have the special if-statement
            to gen 1 layout if there's nothing
            and another if there r meetings
            
            and kv file doesn't allow large if-block or for-loop
            """
            
            parent_label = Label(font_size=60, pos_hint={'center_y': 0.5}, color=self.rgb(237, 151, 76, alpha=1))
            img = Image(source='assets/orange_calendar.png',pos_hint={'center_y': 0.5, 'center_x' : 0.5}, size_hint= (.5,.5), allow_stretch = True)
            #parent_label.add_widget(img)
            layout.add_widget(img)
            
            
            
            layout.add_widget(Label(text='You have no appointments today', font_size=40, pos_hint={'center_y':0.2}, color=self.rgb(237, 151, 76, alpha=1)))
            self.add_widget(layout)
        else:
            # there are content_present meetings to blit onto screen
            """ blit date to screen """
            today = date.today().strftime("%A, %B %d") # 'Friday, June 24'
#            date_grid = GridLayout(cols=2, pos_hint={'top':1, 'x': .1}, size_hint_y= 0.85)
            date_grid = GridLayout(cols=2, row_force_default=True, row_default_height=40, pos_hint = {'x': 0.05, 'top':0.875}, padding=(25, 0))
            date_grid.add_widget(Label(
                text = "Today - " + today,
                color=self.rgb(237, 151, 76),
                font_size=35,
            ))
            date_grid.add_widget(Widget())
            
            meetings = read_data(self.firebase)
            
            item_grid = GridLayout(cols=1, row_force_default=True, row_default_height=100, pos_hint = {'x': 0, 'top':0.8}, padding=(25, 0))
            
           
            for info in meetings:
                # ToDo: if the date isn't today's do we even wanna show it?
                
                #float = FloatLayout(pos=item_grid.pos, size=item_grid.size)
                float = FloatLayout()
                float.add_widget(Label(
                    text = info[0] + '\n' + info[1].strip(),
                    font_size = 20,
                    color = self.rgb(13, 59, 102),
                    
                    size_hint_x = 0.3,
                    pos_hint = {'center_x': 0.05, 'center_y': 0.5}
                    ))
                float.add_widget(Label(
                    text= info[3],
                    font_size = 40,
                    color = self.rgb(13, 59, 102),
                    pos_hint = {'left': 0.2, 'center_y': 0.7},
                ))
                float.add_widget(Label(
                    text= info[4],
                    font_size = 20,
                    color = self.rgb(13, 59, 102),
                    pos_hint = {'left': 0.3, 'center_y': 0.25}
                ))
                item_grid.add_widget(float)
                
                with float.canvas.before:
                    Color(*self.rgb(245, 213, 95))
                    float.rect = Rectangle(pos = float.center, size = (self.width, self.height))
                    Color(*self.rgb(13, 59, 102))
                    float.line = Line(width=2, rectangle=(float.x, float.y, float.width, float.height))
                    
                    float.bind(pos = self.update_background_fill, size=self.update_background_fill)
                    

            
            layout.add_widget(date_grid)
            layout.add_widget(item_grid)
            self.add_widget(layout)
            
    def update_background_fill(self, *args):
        # args[0] is the floatlayout
        args[0].rect.pos = (0, args[0].pos[1])
        args[0].rect.size = (self.size[0], args[0].size[1])
        
        args[0].line.rectangle = (0, args[0].y, self.size[0], args[0].height)
        
        
        """
        above we use self.size (the screen) for x-val and args[0].size (the floatlayout) for the y-val
        we do this bc the FL has 25 padding so the canvas doesn't draw everything, instead we sub in the screen's x so the rect stretches everything
        """
        
    def on_leave(self, *args):
        BottomMenu.save_last_screen('dashboard')
        # layout.clear_widgets()
        

