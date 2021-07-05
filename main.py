from collections import OrderedDict
from io import StringIO
from math import log, sqrt

import numpy as np
import pandas as pd

from bokeh.plotting import figure, output_file, show
from bokeh.models import ColumnDataSource, Div, Select, Slider, TextInput,Panel, Tabs,Button, RangeSlider
from bokeh.io import curdoc
from bokeh.layouts import column, row

from bokeh.models import Panel, Tabs,Button, RangeSlider
from os.path import join,dirname

from panels.htmls.html_config import *

# from panels.circle_img import Circle_Img
#
# circle_figure=dict(title='example individual',plot_width=width, plot_height=height,
#     x_axis_type=None, y_axis_type=None,
#     x_range=(-420, 420), y_range=(-420, 420),
#     min_border=0, outline_line_color="black",
#     background_fill_color="#f0e1d2")
#
# p = circle_fig(stability_dimensions,**circle_figure)

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

Customer_Inputs = (TextInput(title="Customer name contains:"),
                 Select(title="Customer's Group", value="All",
                                  options=["School","NPFT"]),
                 Select(title="Customer", value="All",
                                   options=["Kyle","Reggie"]),)
Group_Inputs = (TextInput(title="Group name contains:"),
                 Select(title="Group", value="All",
                                   options=["School","NPFT"]),)


# button.js_on_click(CustomJS(args=dict(source=source),
#                             code=open(join(dirname(__file__), "download.js")).read()))
cbutton = Button(label="Add Customer", button_type="success")
gbutton = Button(label="Add Group", button_type="success")

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
def df_from_str(str):
    return pd.read_csv(StringIO(str),skiprows=1,skipinitialspace=True,engine='python')
df = df_from_str(stability_dimensions)
Sliders = tuple()
for dim_name in df.Dimension:
    Sliders += (Slider(title=dim_name, start=0, end=5, value=2, step=1),)

inputs1 = column(*[row(slider,Button(label=slider.title, button_type="warning",default_size=40)) for slider in Sliders[:6]])
inputs2 = column(*[row(slider,Button(label=slider.title, button_type="warning",default_size=40)) for slider in Sliders[6:]])

slider = RangeSlider(title="Digital Literacy", start=0, end=5, value=(1, 3), step=1)


if __name__[:10] == "bokeh_app_":
    #nc_desc = div_html("new_customer.html",sizing_mode="stretch_width")
    #survey_desc = div_html("panels/htmls/survey.html",sizing_mode="stretch_width")

    # New_Customer_tab=column(nc_desc,
    #                     row(column(TextInput(title="New Customer"),
    #                             *Group_Inputs,cbutton,width=320),
    #                         column(TextInput(title="New Group"),
    #                             gbutton,width=320)
    #                         )
    #                     )
    from panels.new_customer import New_Customer
    NC = New_Customer(ini_section="local_stability")


    Survey=column(row(survey_desc,
                    column(*Customer_Inputs,width=320)),
                  row(inputs1,inputs2)
                  )
    #
    # Export_Csv=row(column(slider,
    #                     *Group_Inputs,
    #                     Button(label="Add Group", button_type="success")
    #                      )
    #               )

    tab0 = Panel(child=NC.new_customer_panel(), title="New Customer")
    #tab1 = Panel(child=Survey, title="Survey")
    #tab2 = Panel(child=Export_Csv,title="Export CSV")

    l=Tabs(tabs=[tab0])
    curdoc().add_root(l)
