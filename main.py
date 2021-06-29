from collections import OrderedDict
from io import StringIO
from math import log, sqrt

import numpy as np
import pandas as pd

from bokeh.plotting import figure, output_file, show
from bokeh.models import ColumnDataSource, Div, Select, Slider, TextInput
from bokeh.io import curdoc
from bokeh.layouts import column, row

stability_dimensions = """
Dimension,                   Before,          After,        gram
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

drug_color = OrderedDict([
    ("Before",   "#0d3362"),
    ("After", "#c64737"),
])

gram_color = OrderedDict([
    ("negative", "#e69584"),
    ("positive", "#aeaeb8"),
])

df = pd.read_csv(StringIO(stability_dimensions),
                 skiprows=1,
                 skipinitialspace=True,
                 engine='python')
Sliders = tuple()
for dim_name in df.Dimension:
    Sliders += (Slider(title=dim_name, start=0, end=5, value=2, step=1),)


width = 500
height = 500
inner_radius = 90
outer_radius = 300

#minr = sqrt(log(.001 * 1E4))
#maxr = sqrt(log(1000 * 1E4))
minr = 0
maxr = 5
a = (outer_radius - inner_radius) / (minr - maxr)
b = inner_radius - a * maxr

def rad(mic):
    return a * mic + b

big_angle = 2.0 * np.pi / (len(df) + 1)
small_angle = big_angle / 7

p = figure(title='example individual',plot_width=width, plot_height=height,
    x_axis_type=None, y_axis_type=None,
    x_range=(-420, 420), y_range=(-420, 420),
    min_border=0, outline_line_color="black",
    background_fill_color="#f0e1d2")

p.xgrid.grid_line_color = None
p.ygrid.grid_line_color = None

# annular wedges
angles = np.pi/2 - big_angle/2 - df.index.to_series()*big_angle
colors = [gram_color[gram] for gram in df.gram]
p.annular_wedge(
    0, 0, inner_radius, outer_radius, -big_angle+angles, angles, color=colors,
)

# small wedges
p.annular_wedge(0, 0, inner_radius, rad(df.Before),
                -big_angle+angles+5*small_angle, -big_angle+angles+6*small_angle,
                color=drug_color['Before'])
p.annular_wedge(0, 0, inner_radius, rad(df.After),
                -big_angle+angles+3*small_angle, -big_angle+angles+4*small_angle,
                color=drug_color['After'])

# circular axes and lables
#labels = np.power(10.0, np.arange(-3, 4))
labels = np.arange(0,6)
radii = a * labels + b
p.circle(0, 0, radius=radii, fill_color=None, line_color="white")
p.text(0, radii[:-1], [str(r) for r in labels[:-1]],
       text_font_size="11px", text_align="center", text_baseline="middle")

# radial axes
p.annular_wedge(0, 0, inner_radius-10, outer_radius+10,
                -big_angle+angles, -big_angle+angles, color="black")

# bacteria labels
xr = radii[0]*np.cos(np.array(-big_angle/2 + angles))
yr = radii[0]*np.sin(np.array(-big_angle/2 + angles))
label_angle=np.array(-big_angle/2+angles)
label_angle[label_angle < -np.pi/2] += np.pi # easier to read labels on the left side
p.text(xr, yr, df.Dimension, angle=label_angle,
       text_font_size="12px", text_align="center", text_baseline="middle")

# OK, these hand drawn legends are pretty clunky, will be improved in future release
#p.circle([-40, -40], [-370, -390], color=list(gram_color.values()), radius=5)
# p.text([-30, -30], [-370, -390], text=["Gram-" + gr for gr in gram_color.keys()],
#        text_font_size="9px", text_align="left", text_baseline="middle")
#
# p.rect([-40, -40, -40], [18, 0, -18], width=30, height=13,
#        color=list(drug_color.values()))
# p.text([-15, -15, -15], [18, 0, -18], text=list(drug_color),
#        text_font_size="12px", text_align="left", text_baseline="middle")

#output_file("burtin.html", title="burtin.py example")

#show(p)
axis_map = {
    "Digital Literacy":"literacy",
    "Income/Living Wage":"income",
    "Employment Stability":"employability",
    "Childcare":"childcare",
    "English Language Skills":"english",
    "Food Security":"food",
    "Career Resiliency/Training":"skills",
    "Education":"education",
    "Work Clothing":"clothes",
    "Housing":"housing",
    "Personal Safety":"safety",
    "Behavioral Health":"health",
}
x_axis = Select(title="X Axis", options=sorted(axis_map.keys()), value="Digital Literacy")
y_axis = Select(title="Y Axis", options=sorted(axis_map.keys()), value="Employment Stability")
# Create Column Data Source that will be used by the plot
source = ColumnDataSource(data=dict(x=[], y=[], color=[], title=[], year=[], revenue=[], alpha=[]))

TOOLTIPS=[
    ("Name", "@name"),
    ("Group", "@group"),
    ("Income", "@income")
]

p2 = figure(height=600, width=700, title="", toolbar_location=None, tooltips=TOOLTIPS, sizing_mode="scale_both")
p2.circle(x="x", y="y", source=source, size=7, color="color", line_color=None, fill_alpha="alpha")
#desc = Div(text=open(join(dirname(__file__), "description.html")).read(), sizing_mode="stretch_width")
def update():
    pass
#Sliders = (TextInput(title="Group"),)+Sliders

#Sliders = (Select(title="Group", value="All",
#               options=["School","NPFT"]),)+Sliders
#Sliders = (TextInput(title="Customer"),)+Sliders
# i = row(column(Select(title="Group", value="All",
#                options=["School","NPFT"]),
#                TextInput(title="New Group")
#                ))
Customer_Inputs = (TextInput(title="Customer name contains:"),
                 Select(title="Customer", value="All",
                                   options=["Kyle","Reggie"]),
                TextInput(title="New Customer"),)
Group_Inputs = (TextInput(title="Group name contains:"),
                 Select(title="Group", value="All",
                                   options=["School","NPFT"]),
                TextInput(title="New Group"),)
from os.path import join,dirname
#for slider in Sliders:
#    slider.on_change('value', lambda attr, old, new: update())
desc = Div(text=open(join(dirname(__file__), "description.html")).read(), sizing_mode="stretch_width")
inputs1 = column(*Sliders[:6], width=320)
inputs2 = column(*Sliders[6:], width=320)
l=row(column(desc,row(column(*Customer_Inputs,width=320),column(*Group_Inputs,width=320)),row(inputs1,inputs2)),column(p,p2))
curdoc().add_root(l)
