#!/usr/bin/env python
# coding: utf-8


from kivy.lang import Builder
from kivy.uix.screenmanager import Screen

from menu import BottomMenu

from random import randrange

kv = Builder.load_file('statistics.kv')

class Statistics(Screen):
    def on_pre_enter(self, *args):
        self.generate_points()
        
    def on_enter(self, *args):
        self.display_graph()
        
    def generate_points(self, X_MIN=1, X_MAX=50, Y_MIN=0, Y_MAX=100, INTERVAL=10):
        """
        Generate points for an increasing bar-graph
        Customize the min/max's & interval
        Returned for an `kivy.properties.ObservableList`
        
        INTERVAL should be perfectly divisible by both MAX's
        """

        x_intervals = X_MAX // INTERVAL
        y_intervals = list(range(Y_MIN, Y_MAX+1, Y_MAX//INTERVAL))
        points = []
        
        for index, x_interval in enumerate(range(X_MIN, X_MAX, x_intervals)):
            for x_val in range(x_interval, x_interval+x_intervals):
                y_val = randrange(y_intervals[index], y_intervals[index+1])
                points.append((x_val, y_val))
        return points

    def display_graph(self):
        """ throw it on a custom boxlayout and load from kv file
            this way the regular label loads first, box layout can take its time
            w/ imports """
        from graph_util import Graph, SmoothLinePlot, BarPlot
        import itertools
        from math import exp
        from random import randrange
        from kivy.uix.boxlayout import BoxLayout
        
        boxlayout = BoxLayout(orientation='vertical', pos_hint={"top": .8}, size_hint_y=.7)
        # example of a custom theme
        colors = itertools.cycle([
            self.rgb(125, 172, 159), self.rgb(220, 112, 98), self.rgb(102, 168, 212), self.rgb(229, 176, 96)])
        graph_theme = {
            'label_options': {
                'color': self.rgb(13, 59, 102),  # color of tick labels and titles
                'bold': True},
            'tick_color': self.rgb(128, 128, 128),  # ticks and grid
            'border_color': self.rgb(128, 128, 128)}  # border drawn around each graph

        graph = Graph(
            xlabel='ContractFlow Downloads',
            ylabel='Productivity',
            x_ticks_minor=5,
            x_ticks_major=10,
            y_ticks_major=25,
            y_grid_label=True,
            x_grid_label=True,
            padding=5,
            xlog=False,
            ylog=False,
            x_grid=True,
            y_grid=True,
            xmin=0,
            xmax=50,
            ymin=0,
            ymax=100,
            **graph_theme)
            
        plot = BarPlot(color=next(colors), bar_spacing=.72)
        graph.add_plot(plot)
        plot.bind_to_graph(graph)
  
        plot.points = self.generate_points(
                    X_MIN=int(graph.xmin),
                    X_MAX=int(graph.xmax),
                    Y_MIN=int(graph.ymin),
                    Y_MAX=int(graph.ymax),
                    INTERVAL=10)
        print(plot.points)
        
        plot = SmoothLinePlot(color=next(colors))
        plot.points = [(x, .3*exp(.12*x)) for x in range(int(graph.xmin), int(graph.xmax))]
        graph.add_plot(plot)
        
        boxlayout.add_widget(graph)
        self.add_widget(boxlayout)
        
    def rgb(self, r, g, b, alpha=1):
        return BottomMenu.rgb(self, r, g, b, alpha)
        
    def on_pre_leave(self, *args):
        self.manager.transition.direction = 'down'
        BottomMenu.save_last_screen('statistics')
