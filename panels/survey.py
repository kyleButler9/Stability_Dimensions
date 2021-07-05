from panels.psql.config import *
from panels.htmls.html_config import *

from os.path import join,dirname

from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Div, Select, Slider, TextInput,Panel, Tabs,Button, RangeSlider

import numpy as np
import pandas as pd

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
class Survey(DBI):
    def __init__(self,*args,**kwargs):
        DBI.__init__(self,ini_section = kwargs['ini_section'])
    def survey_panel(self):
        panel= (self.desc(),
                row(self.group_name_contains(),
                    self.group_dd(),
                    self.group_notes_description()
                    ),
                row(self.cust_name(),
                    self.cust_address(),
                    self.cust_notes(),
                    self.cust_button()
                    ),
                row(self.new_group(),
                    self.new_group_notes(),
                    self.insert_new_group_button()
                    ),
                )
                column(*Customer_Inputs,width=320)),
              row(inputs1,inputs2)
        return column(*panel)
    def desc(self):
        return div_html("survey.html",sizing_mode="stretch_width")
    def sliders(self):
        inputs1 = column(*[row(slider,Button(label=slider.title, button_type="warning",default_size=40)) for slider in Sliders[:6]])
        inputs2 = column(*[row(slider,Button(label=slider.title, button_type="warning",default_size=40)) for slider in Sliders[6:]])
        return inputs1,inputs2
    def group_name_contains(self):
        self.downsample_groups=TextInput(title="Group name contains:")
        self.downsample_groups.on_change('value', lambda attr, old, new: self.downsample_group_handler())
        return self.downsample_groups
    def downsample_group_handler(self):
        groups = self.fetchall("SELECT name FROM groups WHERE name ~* %s;",
                                self.downsample_groups.value.strip())
        self.group_dropdown.options=[group[0] for group in groups]
    def get_all_groups(self):
        groups = self.fetchall("SELECT name FROM groups;")
        return [group[0] for group in groups]
    def group_dd(self):
        groups = self.get_all_groups()
        self.group_dropdown=Select(title="Group",
                value="All",
                options=groups)
        self.group_dropdown.on_change('value',lambda attr, old, new: self.get_notes())
        return self.group_dropdown
    def cust_name_contains(self):
        self.downsample_cust=TextInput(title="Customer name contains:")
        self.downsample_cust.on_change('value', lambda attr, old, new: self.downsample_cust_handler())
        return self.downsample_groups
    def downsample_cust_handler(self):
        groups = self.fetchall("SELECT name FROM customers WHERE name ~* %s and group ~* %s;",
                                self.downsample_cust.value.strip(),
                                self.group.value)
        self.group_dropdown.options=[group[0] for group in groups]
    def group_dd(self):
        groups = self.get_all_groups()
        self.group_dropdown=Select(title="Group",
                value="All",
                options=groups)
        self.group_dropdown.on_change('value',lambda attr, old, new: self.get_notes())
        return self.group_dropdown
