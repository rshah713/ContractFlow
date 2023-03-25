'''
Graph
======
The graph uses a stencil view to clip the plots to the graph display area.
As with the stencil graphics instructions, you cannot stack more than 8
stencil-aware widgets.
'''

from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.stencilview import StencilView
from kivy.properties import NumericProperty, BooleanProperty,\
    BoundedNumericProperty, StringProperty, ListProperty, ObjectProperty,\
    DictProperty, AliasProperty
from kivy.clock import Clock
from kivy.graphics import Mesh, Color, Rectangle
from kivy.graphics import Fbo
from kivy.graphics.texture import Texture
from kivy.event import EventDispatcher
from kivy.lang import Builder
from kivy.logger import Logger
from kivy import metrics
from math import log10, floor, ceil
from decimal import Decimal

def identity(x):
    return x


def exp10(x):
    return 10 ** x


Builder.load_string("""
<GraphRotatedLabel>:
    canvas.before:
        PushMatrix
        Rotate:
            angle: root.angle
            axis: 0, 0, 1
            origin: root.center
    canvas.after:
        PopMatrix
""")

class GraphRotatedLabel(Label):
    angle = NumericProperty(0)

class Graph(Widget):
    '''Graph class'''

    # triggers a full reload of graphics
    _trigger = ObjectProperty(None)
    # triggers only a repositioning of objects due to size/pos updates
    _trigger_size = ObjectProperty(None)
    # triggers only a update of colors, e.g. tick_color
    _trigger_color = ObjectProperty(None)
    # holds widget with the x-axis label
    _xlabel = ObjectProperty(None)
    # holds widget with the y-axis label
    _ylabel = ObjectProperty(None)
    # holds all the x-axis tick mark labels
    _x_grid_label = ListProperty([])
    # holds all the y-axis tick mark labels
    _y_grid_label = ListProperty([])
    # the mesh drawing all the ticks/grids
    _mesh_ticks = ObjectProperty(None)
    # the mesh which draws the surrounding rectangle
    _mesh_rect = ObjectProperty(None)
    # a list of locations of major and minor ticks. The values are not
    # but is in the axis min - max range
    _ticks_majorx = ListProperty([])
    _ticks_minorx = ListProperty([])
    _ticks_majory = ListProperty([])
    _ticks_minory = ListProperty([])

    tick_color = ListProperty([.25, .25, .25, 1])
    background_color = ListProperty([0, 0, 0, 0])
    border_color = ListProperty([1, 1, 1, 1])
    label_options = DictProperty()
    _with_stencilbuffer = BooleanProperty(True)
    def __init__(self, **kwargs):
        super(Graph, self).__init__(**kwargs)

        with self.canvas:
            self._fbo = Fbo(size=self.size, with_stencilbuffer=self._with_stencilbuffer)

        with self._fbo:
            self._background_color = Color(*self.background_color)
            self._background_rect = Rectangle(size=self.size)
            self._mesh_ticks_color = Color(*self.tick_color)
            self._mesh_ticks = Mesh(mode='lines')
            self._mesh_rect_color = Color(*self.border_color)
            self._mesh_rect = Mesh(mode='line_strip')

        with self.canvas:
            Color(1, 1, 1)
            self._fbo_rect = Rectangle(size=self.size, texture=self._fbo.texture)

        mesh = self._mesh_rect
        mesh.vertices = [0] * (5 * 4)
        mesh.indices = range(5)

        self._plot_area = StencilView()
        self.add_widget(self._plot_area)

        t = self._trigger = Clock.create_trigger(self._redraw_all)
        ts = self._trigger_size = Clock.create_trigger(self._redraw_size)
        tc = self._trigger_color = Clock.create_trigger(self._update_colors)

        self.bind(center=ts, padding=ts, precision=ts, plots=ts, x_grid=ts,
                  y_grid=ts, draw_border=ts)
        self.bind(xmin=t, xmax=t, xlog=t, x_ticks_major=t, x_ticks_minor=t,
                  xlabel=t, x_grid_label=t, ymin=t, ymax=t, ylog=t,
                  y_ticks_major=t, y_ticks_minor=t, ylabel=t, y_grid_label=t,
                  font_size=t, label_options=t, x_ticks_angle=t)
        self.bind(tick_color=tc, background_color=tc, border_color=tc)
        self._trigger()

    def add_widget(self, widget):
        if widget is self._plot_area:
            canvas = self.canvas
            self.canvas = self._fbo
        super(Graph, self).add_widget(widget)
        if widget is self._plot_area:
            self.canvas = canvas

    def remove_widget(self, widget):
        if widget is self._plot_area:
            canvas = self.canvas
            self.canvas = self._fbo
        super(Graph, self).remove_widget(widget)
        if widget is self._plot_area:
            self.canvas = canvas

    def _get_ticks(self, major, minor, log, s_min, s_max):
        if major and s_max > s_min:
            if log:
                s_min = log10(s_min)
                s_max = log10(s_max)
                # count the decades in min - max. This is in actual decades,
                # not logs.
                n_decades = floor(s_max - s_min)
                # for the fractional part of the last decade, we need to
                # convert the log value, x, to 10**x but need to handle
                # differently if the last incomplete decade has a decade
                # boundary in it
                if floor(s_min + n_decades) != floor(s_max):
                    n_decades += 1 - (10 ** (s_min + n_decades + 1) - 10 **
                                      s_max) / 10 ** floor(s_max + 1)
                else:
                    n_decades += ((10 ** s_max - 10 ** (s_min + n_decades)) /
                                  10 ** floor(s_max + 1))
                # this might be larger than what is needed, but we delete
                # excess later
                n_ticks_major = n_decades / float(major)
                n_ticks = int(floor(n_ticks_major * (minor if minor >=
                                                     1. else 1.0))) + 2
                # in decade multiples, e.g. 0.1 of the decade, the distance
                # between ticks
                decade_dist = major / float(minor if minor else 1.0)

                points_minor = [0] * n_ticks
                points_major = [0] * n_ticks
                k = 0  # position in points major
                k2 = 0  # position in points minor
                # because each decade is missing 0.1 of the decade, if a tick
                # falls in < min_pos skip it
                min_pos = 0.1 - 0.00001 * decade_dist
                s_min_low = floor(s_min)
                # first real tick location. value is in fractions of decades
                # from the start we have to use decimals here, otherwise
                # floating point inaccuracies results in bad values
                start_dec = ceil((10 ** Decimal(s_min - s_min_low - 1)) /
                                 Decimal(decade_dist)) * decade_dist
                count_min = (0 if not minor else
                             floor(start_dec / decade_dist) % minor)
                start_dec += s_min_low
                count = 0  # number of ticks we currently have passed start
                while True:
                    # this is the current position in decade that we are.
                    # e.g. -0.9 means that we're at 0.1 of the 10**ceil(-0.9)
                    # decade
                    pos_dec = start_dec + decade_dist * count
                    pos_dec_low = floor(pos_dec)
                    diff = pos_dec - pos_dec_low
                    zero = abs(diff) < 0.001 * decade_dist
                    if zero:
                        # the same value as pos_dec but in log scale
                        pos_log = pos_dec_low
                    else:
                        pos_log = log10((pos_dec - pos_dec_low
                                         ) * 10 ** ceil(pos_dec))
                    if pos_log > s_max:
                        break
                    count += 1
                    if zero or diff >= min_pos:
                        if minor and not count_min % minor:
                            points_major[k] = pos_log
                            k += 1
                        else:
                            points_minor[k2] = pos_log
                            k2 += 1
                    count_min += 1
            else:
                # distance between each tick
                tick_dist = major / float(minor if minor else 1.0)
                n_ticks = int(floor((s_max - s_min) / tick_dist) + 1)
                points_major = [0] * int(floor((s_max - s_min) / float(major))
                                         + 1)
                points_minor = [0] * (n_ticks - len(points_major) + 1)
                k = 0  # position in points major
                k2 = 0  # position in points minor
                for m in range(0, n_ticks):
                    if minor and m % minor:
                        points_minor[k2] = m * tick_dist + s_min
                        k2 += 1
                    else:
                        points_major[k] = m * tick_dist + s_min
                        k += 1
            del points_major[k:]
            del points_minor[k2:]
        else:
            points_major = []
            points_minor = []
        return points_major, points_minor

    def _update_labels(self):
        xlabel = self._xlabel
        ylabel = self._ylabel
        x = self.x
        y = self.y
        width = self.width
        height = self.height
        padding = self.padding
        x_next = padding + x
        y_next = padding + y
        xextent = width + x
        yextent = height + y
        ymin = self.ymin
        ymax = self.ymax
        xmin = self.xmin
        precision = self.precision
        x_overlap = False
        y_overlap = False
        # set up x and y axis labels
        if xlabel:
            xlabel.text = self.xlabel
            xlabel.texture_update()
            xlabel.size = xlabel.texture_size
            xlabel.pos = int(x + width / 2. - xlabel.width / 2.), int(padding + y)
            y_next += padding + xlabel.height
        if ylabel:
            ylabel.text = self.ylabel
            ylabel.texture_update()
            ylabel.size = ylabel.texture_size
            ylabel.x = padding + x - (ylabel.width / 2. - ylabel.height / 2.)
            x_next += padding + ylabel.height
        xpoints = self._ticks_majorx
        xlabels = self._x_grid_label
        xlabel_grid = self.x_grid_label
        ylabel_grid = self.y_grid_label
        ypoints = self._ticks_majory
        ylabels = self._y_grid_label
        # now x and y tick mark labels
        if len(ylabels) and ylabel_grid:
            # horizontal size of the largest tick label, to have enough room
            funcexp = exp10 if self.ylog else identity
            funclog = log10 if self.ylog else identity
            ylabels[0].text = precision % funcexp(ypoints[0])
            ylabels[0].texture_update()
            y1 = ylabels[0].texture_size
            y_start = y_next + (padding + y1[1] if len(xlabels) and xlabel_grid
                                else 0) + \
                               (padding + y1[1] if not y_next else 0)
            yextent = y + height - padding - y1[1] / 2.

            ymin = funclog(ymin)
            ratio = (yextent - y_start) / float(funclog(ymax) - ymin)
            y_start -= y1[1] / 2.
            y1 = y1[0]
            for k in range(len(ylabels)):
                ylabels[k].text = precision % funcexp(ypoints[k])
                ylabels[k].texture_update()
                ylabels[k].size = ylabels[k].texture_size
                y1 = max(y1, ylabels[k].texture_size[0])
                ylabels[k].pos = (
                    int(x_next),
                    int(y_start + (ypoints[k] - ymin) * ratio))
            if len(ylabels) > 1 and ylabels[0].top > ylabels[1].y:
                y_overlap = True
            else:
                x_next += y1 + padding
        if len(xlabels) and xlabel_grid:
            funcexp = exp10 if self.xlog else identity
            funclog = log10 if self.xlog else identity
            # find the distance from the end that'll fit the last tick label
            xlabels[0].text = precision % funcexp(xpoints[-1])
            xlabels[0].texture_update()
            xextent = x + width - xlabels[0].texture_size[0] / 2. - padding
            # find the distance from the start that'll fit the first tick label
            if not x_next:
                xlabels[0].text = precision % funcexp(xpoints[0])
                xlabels[0].texture_update()
                x_next = padding + xlabels[0].texture_size[0] / 2.
            xmin = funclog(xmin)
            ratio = (xextent - x_next) / float(funclog(self.xmax) - xmin)
            right = -1
            for k in range(len(xlabels)):
                xlabels[k].text = precision % funcexp(xpoints[k])
                # update the size so we can center the labels on ticks
                xlabels[k].texture_update()
                xlabels[k].size = xlabels[k].texture_size
                half_ts = xlabels[k].texture_size[0] / 2.
                xlabels[k].pos = (
                    int(x_next + (xpoints[k] - xmin) * ratio - half_ts),
                    int(y_next))
                if xlabels[k].x < right:
                    x_overlap = True
                    break
                right = xlabels[k].right
            if not x_overlap:
                y_next += padding + xlabels[0].texture_size[1]
        # now re-center the x and y axis labels
        if xlabel:
            xlabel.x = int(x_next + (xextent - x_next) / 2. - xlabel.width / 2.)
        if ylabel:
            ylabel.y = int(y_next + (yextent - y_next) / 2. - ylabel.height / 2.)
            ylabel.angle = 90
        if x_overlap:
            for k in range(len(xlabels)):
                xlabels[k].text = ''
        if y_overlap:
            for k in range(len(ylabels)):
                ylabels[k].text = ''
        return x_next - x, y_next - y, xextent - x, yextent - y

    def _update_ticks(self, size):
        # re-compute the positions of the bounding rectangle
        mesh = self._mesh_rect
        vert = mesh.vertices
        if self.draw_border:
            s0, s1, s2, s3 = size
            vert[0] = s0
            vert[1] = s1
            vert[4] = s2
            vert[5] = s1
            vert[8] = s2
            vert[9] = s3
            vert[12] = s0
            vert[13] = s3
            vert[16] = s0
            vert[17] = s1
        else:
            vert[0:18] = [0 for k in range(18)]
        mesh.vertices = vert
        # re-compute the positions of the x/y axis ticks
        mesh = self._mesh_ticks
        vert = mesh.vertices
        start = 0
        xpoints = self._ticks_majorx
        ypoints = self._ticks_majory
        xpoints2 = self._ticks_minorx
        ypoints2 = self._ticks_minory
        ylog = self.ylog
        xlog = self.xlog
        xmin = self.xmin
        xmax = self.xmax
        if xlog:
            xmin = log10(xmin)
            xmax = log10(xmax)
        ymin = self.ymin
        ymax = self.ymax
        if ylog:
            ymin = log10(ymin)
            ymax = log10(ymax)
        if len(xpoints):
            top = size[3] if self.x_grid else metrics.dp(12) + size[1]
            ratio = (size[2] - size[0]) / float(xmax - xmin)
            for k in range(start, len(xpoints) + start):
                vert[k * 8] = size[0] + (xpoints[k - start] - xmin) * ratio
                vert[k * 8 + 1] = size[1]
                vert[k * 8 + 4] = vert[k * 8]
                vert[k * 8 + 5] = top
            start += len(xpoints)
        if len(xpoints2):
            top = metrics.dp(8) + size[1]
            ratio = (size[2] - size[0]) / float(xmax - xmin)
            for k in range(start, len(xpoints2) + start):
                vert[k * 8] = size[0] + (xpoints2[k - start] - xmin) * ratio
                vert[k * 8 + 1] = size[1]
                vert[k * 8 + 4] = vert[k * 8]
                vert[k * 8 + 5] = top
            start += len(xpoints2)
        if len(ypoints):
            top = size[2] if self.y_grid else metrics.dp(12) + size[0]
            ratio = (size[3] - size[1]) / float(ymax - ymin)
            for k in range(start, len(ypoints) + start):
                vert[k * 8 + 1] = size[1] + (ypoints[k - start] - ymin) * ratio
                vert[k * 8 + 5] = vert[k * 8 + 1]
                vert[k * 8] = size[0]
                vert[k * 8 + 4] = top
            start += len(ypoints)
        if len(ypoints2):
            top = metrics.dp(8) + size[0]
            ratio = (size[3] - size[1]) / float(ymax - ymin)
            for k in range(start, len(ypoints2) + start):
                vert[k * 8 + 1] = size[1] + (ypoints2[k - start] - ymin) * ratio
                vert[k * 8 + 5] = vert[k * 8 + 1]
                vert[k * 8] = size[0]
                vert[k * 8 + 4] = top
        mesh.vertices = vert

    x_axis = ListProperty([None])
    y_axis = ListProperty([None])

    def get_x_axis(self, axis=0):
        if axis == 0:
            return self.xlog, self.xmin, self.xmax
        info = self.x_axis[axis]
        return (info["log"], info["min"], info["max"])

    def get_y_axis(self, axis=0):
        if axis == 0:
            return self.ylog, self.ymin, self.ymax
        info = self.y_axis[axis]
        return (info["log"], info["min"], info["max"])

    def add_x_axis(self, xmin, xmax, xlog=False):
        data = {
            "log": xlog,
            "min": xmin,
            "max": xmax
        }
        self.x_axis.append(data)
        return data

    def add_y_axis(self, ymin, ymax, ylog=False):
        data = {
            "log": ylog,
            "min": ymin,
            "max": ymax
        }
        self.y_axis.append(data)
        return data

    def _update_plots(self, size):
        for plot in self.plots:
            xlog, xmin, xmax = self.get_x_axis(plot.x_axis)
            ylog, ymin, ymax = self.get_y_axis(plot.y_axis)
            plot._update(xlog, xmin, xmax, ylog, ymin, ymax, size)

    def _update_colors(self, *args):
        self._mesh_ticks_color.rgba = tuple(self.tick_color)
        self._background_color.rgba = tuple(self.background_color)
        self._mesh_rect_color.rgba = tuple(self.border_color)

    def _redraw_all(self, *args):
        # add/remove all the required labels
        xpoints_major, xpoints_minor = self._redraw_x(*args)
        ypoints_major, ypoints_minor = self._redraw_y(*args)

        mesh = self._mesh_ticks
        n_points = (len(xpoints_major) + len(xpoints_minor) +
                    len(ypoints_major) + len(ypoints_minor))
        mesh.vertices = [0] * (n_points * 8)
        mesh.indices = [k for k in range(n_points * 2)]
        self._redraw_size()

    def _redraw_x(self, *args):
        font_size = self.font_size
        if self.xlabel:
            xlabel = self._xlabel
            if not xlabel:
                xlabel = Label()
                self.add_widget(xlabel)
                self._xlabel = xlabel

            xlabel.font_size = font_size
            for k, v in self.label_options.items():
                setattr(xlabel, k, v)

        else:
            xlabel = self._xlabel
            if xlabel:
                self.remove_widget(xlabel)
                self._xlabel = None
        grids = self._x_grid_label
        xpoints_major, xpoints_minor = self._get_ticks(self.x_ticks_major,
                                                       self.x_ticks_minor,
                                                       self.xlog, self.xmin,
                                                       self.xmax)
        self._ticks_majorx = xpoints_major
        self._ticks_minorx = xpoints_minor

        if not self.x_grid_label:
            n_labels = 0
        else:
            n_labels = len(xpoints_major)

        for k in range(n_labels, len(grids)):
            self.remove_widget(grids[k])
        del grids[n_labels:]

        grid_len = len(grids)
        grids.extend([None] * (n_labels - len(grids)))
        for k in range(grid_len, n_labels):
            grids[k] = GraphRotatedLabel(
                font_size=font_size, angle=self.x_ticks_angle,
                **self.label_options)
            self.add_widget(grids[k])
        return xpoints_major, xpoints_minor

    def _redraw_y(self, *args):
        font_size = self.font_size
        if self.ylabel:
            ylabel = self._ylabel
            if not ylabel:
                ylabel = GraphRotatedLabel()
                self.add_widget(ylabel)
                self._ylabel = ylabel

            ylabel.font_size = font_size
            for k, v in self.label_options.items():
                setattr(ylabel, k, v)
        else:
            ylabel = self._ylabel
            if ylabel:
                self.remove_widget(ylabel)
                self._ylabel = None
        grids = self._y_grid_label
        ypoints_major, ypoints_minor = self._get_ticks(self.y_ticks_major,
                                                       self.y_ticks_minor,
                                                       self.ylog, self.ymin,
                                                       self.ymax)
        self._ticks_majory = ypoints_major
        self._ticks_minory = ypoints_minor

        if not self.y_grid_label:
            n_labels = 0
        else:
            n_labels = len(ypoints_major)

        for k in range(n_labels, len(grids)):
            self.remove_widget(grids[k])
        del grids[n_labels:]

        grid_len = len(grids)
        grids.extend([None] * (n_labels - len(grids)))
        for k in range(grid_len, n_labels):
            grids[k] = Label(font_size=font_size, **self.label_options)
            self.add_widget(grids[k])
        return ypoints_major, ypoints_minor

    def _redraw_size(self, *args):
        # size a 4-tuple describing the bounding box in which we can draw
        # graphs, it's (x0, y0, x1, y1), which correspond with the bottom left
        # and top right corner locations, respectively
        self._clear_buffer()
        size = self._update_labels()
        self.view_pos = self._plot_area.pos = (size[0], size[1])
        self.view_size = self._plot_area.size = (
            size[2] - size[0], size[3] - size[1])

        if self.size[0] and self.size[1]:
            self._fbo.size = self.size
        else:
            self._fbo.size = 1, 1  # gl errors otherwise
        self._fbo_rect.texture = self._fbo.texture
        self._fbo_rect.size = self.size
        self._fbo_rect.pos = self.pos
        self._background_rect.size = self.size
        self._update_ticks(size)
        self._update_plots(size)

    def _clear_buffer(self, *largs):
        fbo = self._fbo
        fbo.bind()
        fbo.clear_buffer()
        fbo.release()

    def add_plot(self, plot):
        '''Add a new plot to this graph.'''
        if plot in self.plots:
            return
        add = self._plot_area.canvas.add
        for instr in plot.get_drawings():
            add(instr)
        plot.bind(on_clear_plot=self._clear_buffer)
        self.plots.append(plot)

    def remove_plot(self, plot):
        '''Remove a plot from this graph.'''
        if plot not in self.plots:
            return
        remove = self._plot_area.canvas.remove
        for instr in plot.get_drawings():
            remove(instr)
        plot.unbind(on_clear_plot=self._clear_buffer)
        self.plots.remove(plot)
        self._clear_buffer()

    def collide_plot(self, x, y):
        '''Determine if the given coordinates fall inside the plot area. '''
        adj_x, adj_y = x - self._plot_area.pos[0], y - self._plot_area.pos[1]
        return 0 <= adj_x <= self._plot_area.size[0] \
            and 0 <= adj_y <= self._plot_area.size[1]

    def to_data(self, x, y):
        '''Convert widget coords to data coords.
        If the graph has multiple axes, use :class:`Plot.unproject` instead.
        '''
        adj_x = float(x - self._plot_area.pos[0])
        adj_y = float(y - self._plot_area.pos[1])
        norm_x = adj_x / self._plot_area.size[0]
        norm_y = adj_y / self._plot_area.size[1]
        if self.xlog:
            xmin, xmax = log10(self.xmin), log10(self.xmax)
            conv_x = 10.**(norm_x * (xmax - xmin) + xmin)
        else:
            conv_x = norm_x * (self.xmax - self.xmin) + self.xmin
        if self.ylog:
            ymin, ymax = log10(self.ymin), log10(self.ymax)
            conv_y = 10.**(norm_y * (ymax - ymin) + ymin)
        else:
            conv_y = norm_y * (self.ymax - self.ymin) + self.ymin
        return [conv_x, conv_y]

    xmin = NumericProperty(0.)
    xmax = NumericProperty(100.)
    xlog = BooleanProperty(False)
    x_ticks_major = BoundedNumericProperty(0, min=0)
    x_ticks_minor = BoundedNumericProperty(0, min=0)
    x_grid = BooleanProperty(False)
    x_grid_label = BooleanProperty(False)
    xlabel = StringProperty('')
    ymin = NumericProperty(0.)
    ymax = NumericProperty(100.)
    ylog = BooleanProperty(False)
    y_ticks_major = BoundedNumericProperty(0, min=0)
    y_ticks_minor = BoundedNumericProperty(0, min=0)
    y_grid = BooleanProperty(False)
    y_grid_label = BooleanProperty(False)
    ylabel = StringProperty('')
    padding = NumericProperty('5dp')
    font_size = NumericProperty('15sp')
    x_ticks_angle = NumericProperty(0)
    precision = StringProperty('%g')
    draw_border = BooleanProperty(True)
    plots = ListProperty([])
    view_size = ObjectProperty((0, 0))
    view_pos = ObjectProperty((0, 0))
 


class Plot(EventDispatcher):

    __events__ = ('on_clear_plot', )

    # most recent values of the params used to draw the plot
    params = DictProperty({'xlog': False, 'xmin': 0, 'xmax': 100,
                           'ylog': False, 'ymin': 0, 'ymax': 100,
                           'size': (0, 0, 0, 0)})
    color = ListProperty([1, 1, 1, 1])
    points = ListProperty([])
    x_axis = NumericProperty(0)
    y_axis = NumericProperty(0)


    def __init__(self, **kwargs):
        super(Plot, self).__init__(**kwargs)
        self.ask_draw = Clock.create_trigger(self.draw)
        self.bind(params=self.ask_draw, points=self.ask_draw)
        self._drawings = self.create_drawings()

    def funcx(self):
        """Return a function that convert or not the X value according to plot
        prameters"""
        return log10 if self.params["xlog"] else lambda x: x

    def funcy(self):
        return log10 if self.params["ylog"] else lambda y: y

    def x_px(self):

        funcx = self.funcx()
        params = self.params
        size = params["size"]
        xmin = funcx(params["xmin"])
        xmax = funcx(params["xmax"])
        ratiox = (size[2] - size[0]) / float(xmax - xmin)
        return lambda x: (funcx(x) - xmin) * ratiox + size[0]

    def y_px(self):
        funcy = self.funcy()
        params = self.params
        size = params["size"]
        ymin = funcy(params["ymin"])
        ymax = funcy(params["ymax"])
        ratioy = (size[3] - size[1]) / float(ymax - ymin)
        return lambda y: (funcy(y) - ymin) * ratioy + size[1]

    def unproject(self, x, y):
        """Return a function that unproject a pixel to a X/Y value on the plot
        """
        params = self.params
        size = params["size"]
        xmin = params["xmin"]
        xmax = params["xmax"]
        ymin = params["ymin"]
        ymax = params["ymax"]
        ratiox = (size[2] - size[0]) / float(xmax - xmin)
        ratioy = (size[3] - size[1]) / float(ymax - ymin)
        x0 = (x - size[0]) / ratiox + xmin
        y0 = (y - size[1]) / ratioy + ymin
        return x0, y0

    def get_px_bounds(self):
        """Returns a dict containing the pixels bounds from the plot parameters.
         The returned values are relative to the graph pos.
        """
        params = self.params
        x_px = self.x_px()
        y_px = self.y_px()
        return {
            "xmin": x_px(params["xmin"]),
            "xmax": x_px(params["xmax"]),
            "ymin": y_px(params["ymin"]),
            "ymax": y_px(params["ymax"]),
        }

    def update(self, xlog, xmin, xmax, ylog, ymin, ymax, size):
        self.params.update({
            'xlog': xlog, 'xmin': xmin, 'xmax': xmax, 'ylog': ylog,
            'ymin': ymin, 'ymax': ymax, 'size': size})

    def get_group(self):
        return ''

    def get_drawings(self):
        if isinstance(self._drawings, (tuple, list)):
            return self._drawings
        return []

    def create_drawings(self):
        pass

    def draw(self, *largs):
        self.dispatch('on_clear_plot')

    def iterate_points(self):
        x_px = self.x_px()
        y_px = self.y_px()
        for x, y in self.points:
            yield x_px(x), y_px(y)

    def on_clear_plot(self, *largs):
        pass

    # compatibility layer
    _update = update
    _get_drawings = get_drawings
    _params = params


class SmoothLinePlot(Plot):
    '''Smooth Plot class, see module documentation for more information.
    This plot use a specific Fragment shader for a custom anti aliasing.
    '''

    SMOOTH_FS = '''
    $HEADER$

    void main(void) {
        float edgewidth = 0.015625 * 64.;
        float t = texture2D(texture0, tex_coord0).r;
        float e = smoothstep(0., edgewidth, t);
        gl_FragColor = frag_color * vec4(1, 1, 1, e);
    }
    '''

    # XXX This gradient data is a 64x1 RGB image, and
    # values goes from 0 -> 255 -> 0.
    GRADIENT_DATA = (
        b"\x00\x00\x00\x07\x07\x07\x0f\x0f\x0f\x17\x17\x17\x1f\x1f\x1f"
        b"'''///777???GGGOOOWWW___gggooowww\x7f\x7f\x7f\x87\x87\x87"
        b"\x8f\x8f\x8f\x97\x97\x97\x9f\x9f\x9f\xa7\xa7\xa7\xaf\xaf\xaf"
        b"\xb7\xb7\xb7\xbf\xbf\xbf\xc7\xc7\xc7\xcf\xcf\xcf\xd7\xd7\xd7"
        b"\xdf\xdf\xdf\xe7\xe7\xe7\xef\xef\xef\xf7\xf7\xf7\xff\xff\xff"
        b"\xf6\xf6\xf6\xee\xee\xee\xe6\xe6\xe6\xde\xde\xde\xd5\xd5\xd5"
        b"\xcd\xcd\xcd\xc5\xc5\xc5\xbd\xbd\xbd\xb4\xb4\xb4\xac\xac\xac"
        b"\xa4\xa4\xa4\x9c\x9c\x9c\x94\x94\x94\x8b\x8b\x8b\x83\x83\x83"
        b"{{{sssjjjbbbZZZRRRJJJAAA999111)))   \x18\x18\x18\x10\x10\x10"
        b"\x08\x08\x08\x00\x00\x00")

    def create_drawings(self):
        from kivy.graphics import Line, RenderContext

        # very first time, create a texture for the shader
        if not hasattr(SmoothLinePlot, '_texture'):
            tex = Texture.create(size=(1, 64), colorfmt='rgb')
            tex.add_reload_observer(SmoothLinePlot._smooth_reload_observer)
            SmoothLinePlot._texture = tex
            SmoothLinePlot._smooth_reload_observer(tex)

        self._grc = RenderContext(
            fs=SmoothLinePlot.SMOOTH_FS,
            use_parent_modelview=True,
            use_parent_projection=True)
        with self._grc:
            self._gcolor = Color(*self.color)
            self._gline = Line(
                points=[], cap='none', width=2.,
                texture=SmoothLinePlot._texture)

        return [self._grc]

    @staticmethod
    def _smooth_reload_observer(texture):
        texture.blit_buffer(SmoothLinePlot.GRADIENT_DATA, colorfmt="rgb")

    def draw(self, *args):
        super(SmoothLinePlot, self).draw(*args)
        # flatten the list
        points = []
        for x, y in self.iterate_points():
            points += [x, y]
        self._gline.points = points

class BarPlot(Plot):
    '''BarPlot class which displays a bar graph.
    '''

    bar_width = NumericProperty(1)
    bar_spacing = NumericProperty(1.)
    graph = ObjectProperty(allownone=True)

    def __init__(self, *ar, **kw):
        super(BarPlot, self).__init__(*ar, **kw)
        self.bind(bar_width=self.ask_draw)
        self.bind(points=self.update_bar_width)
        self.bind(graph=self.update_bar_width)

    def update_bar_width(self, *ar):
        if not self.graph:
            return
        if len(self.points) < 2:
            return
        if self.graph.xmax == self.graph.xmin:
            return

        point_width = (
            len(self.points) *
            float(abs(self.graph.xmax) + abs(self.graph.xmin)) /
            float(abs(max(self.points)[0]) + abs(min(self.points)[0])))

        if not self.points:
            self.bar_width = 1
        else:
            self.bar_width = (
                (self.graph.width - self.graph.padding) /
                point_width * self.bar_spacing)

    def create_drawings(self):
        self._color = Color(*self.color)
        self._mesh = Mesh()
        self.bind(color=lambda instr, value: setattr(self._color, 'rgba', value))
        return [self._color, self._mesh]

    def draw(self, *args):
        super(BarPlot, self).draw(*args)
        points = self.points

        # The mesh only supports (2^16) - 1 indices, so...
        if len(points) * 6 > 65535:
            Logger.error(
                "BarPlot: cannot support more than 10922 points. "
                "Ignoring extra points.")
            points = points[:10922]

        point_len = len(points)
        mesh = self._mesh
        mesh.mode = 'triangles'
        vert = mesh.vertices
        ind = mesh.indices
        diff = len(points) * 6 - len(vert) // 4
        if diff < 0:
            del vert[4 * point_len:]
            del ind[point_len:]
        elif diff > 0:
            ind.extend(range(len(ind), len(ind) + diff))
            vert.extend([0] * (diff * 4))

        bounds = self.get_px_bounds()
        x_px = self.x_px()
        y_px = self.y_px()
        ymin = y_px(0)

        bar_width = self.bar_width
        if bar_width < 0:
            bar_width = x_px(bar_width) - bounds["xmin"]

        for k in range(point_len):
            p = points[k]
            x1 = x_px(p[0])
            x2 = x1 + bar_width
            y1 = ymin
            y2 = y_px(p[1])

            idx = k * 24
            # first triangle
            vert[idx] = x1
            vert[idx + 1] = y2
            vert[idx + 4] = x1
            vert[idx + 5] = y1
            vert[idx + 8] = x2
            vert[idx + 9] = y1
            # second triangle
            vert[idx + 12] = x1
            vert[idx + 13] = y2
            vert[idx + 16] = x2
            vert[idx + 17] = y2
            vert[idx + 20] = x2
            vert[idx + 21] = y1
        mesh.vertices = vert

    def _unbind_graph(self, graph):
        graph.unbind(width=self.update_bar_width,
                     xmin=self.update_bar_width,
                     ymin=self.update_bar_width)

    def bind_to_graph(self, graph):
        old_graph = self.graph

        if old_graph:
            # unbind from the old one
            self._unbind_graph(old_graph)

        # bind to the new one
        self.graph = graph
        graph.bind(width=self.update_bar_width,
                   xmin=self.update_bar_width,
                   ymin=self.update_bar_width)

    def unbind_from_graph(self):
        if self.graph:
            self._unbind_graph(self.graph)
