from collections import OrderedDict
from io import StringIO
from math import log, sqrt

import numpy as np
import pandas as pd

from bokeh.plotting import Figure,show

width = 500
height = 500
class Circle_Img(Figure):
    inner_radius = 90
    outer_radius = 300
    minr = 0
    maxr = 5
    a = (outer_radius - inner_radius) / (minr - maxr)
    b = inner_radius - a * maxr

    bool_color = OrderedDict([
        ("negative", "#e69584"),
        ("positive", "#aeaeb8"),
    ])
    bar_color = OrderedDict([
        ("First",   "#0d3362"),
        ("Second", "#c64737"),
    ])
    def __init__(self,dfstr,*args,**kwargs):
        self.df=self.set_df(dfstr)
        big_angle = 2.0 * np.pi / (len(self.df) + 1)
        small_angle = big_angle / 7
        angles = np.pi/2 - big_angle/2 - self.df.index.to_series()*big_angle
        colors = [self.bool_color[bool] for bool in self.df.improvement]
        Figure.__init__(self,*args,**kwargs)
        self.xgrid.grid_line_color = None
        self.ygrid.grid_line_color = None
        self.annular_wedge(
            0, 0, self.inner_radius, self.outer_radius, -big_angle+angles, angles, color=colors,
        )
        # small wedges
        self.annular_wedge(0, 0, self.inner_radius, self.rad(self.df.Before),
                        -big_angle+angles+5*small_angle, -big_angle+angles+6*small_angle,
                        color=self.bar_color['First'])
        self.annular_wedge(0, 0, self.inner_radius, self.rad(self.df.After),
                        -big_angle+angles+3*small_angle, -big_angle+angles+4*small_angle,
                        color=self.bar_color['Second'])
        # circular axes and lables
        #labels = np.power(10.0, np.arange(-3, 4))
        labels = np.arange(0,6)
        radii = self.a * labels + self.b
        self.circle(0, 0, radius=radii, fill_color=None, line_color="white")
        self.text(0, radii[:-1], [str(r) for r in labels[:-1]],
               text_font_size="11px", text_align="center", text_baseline="middle")

        # radial axes
        self.annular_wedge(0, 0,self. inner_radius-10, self.outer_radius+10,
                        -big_angle+angles, -big_angle+angles, color="black")

        # dimension labels
        xr = radii[0]*np.cos(np.array(-big_angle/2 + angles))
        yr = radii[0]*np.sin(np.array(-big_angle/2 + angles))
        label_angle=np.array(-big_angle/2+angles)
        label_angle[label_angle < -np.pi/2] += np.pi # easier to read labels on the left side
        self.text(xr, yr, df.Dimension, angle=label_angle,
               text_font_size="12px", text_align="center", text_baseline="middle")

    def rad(self,mic):
        return self.a * mic + self.b
    def set_df(self,str):
        return self.df_from_str(str)
    def df_from_str(self,str):
        return pd.read_csv(StringIO(str),skiprows=1,skipinitialspace=True,engine='python')
if __name__ == "__main__":
    stability_dimensions = """
    Dimension,                   Before,          After,   improvement
    Digital Literacy,                   2,            4,    negative
    Income/Living Wage,                 3,            5,    positive
    Employment Stability,               2,            4,    negative
    Childcare,                          1,            5,    positive
    English Language Skills,            2,            5,    positive
    Food Security,                      3,            4,    negative
    Career Resiliency/Training,         2,            5,    negative
    Education,                          2,            5,    negative
    Work Clothing,                      3,            1,    negative
    Housing,                            1,            4,    negative
    Personal Safety,                    2,            5,    negative
    Behavioral Health,                  2,            4,    negative
    """
    circle_figure=dict(title='example individual',plot_width=width, plot_height=height,
        x_axis_type=None, y_axis_type=None,
        x_range=(-420, 420), y_range=(-420, 420),
        min_border=0, outline_line_color="black",
        background_fill_color="#f0e1d2")

    p = Circle_Img(stability_dimensions,**circle_figure)
    show(p)
