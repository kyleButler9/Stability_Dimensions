from bokeh.models import Panel, Tabs
from bokeh.io import curdoc
from bokeh.layouts import column, row

from os.path import join,dirname

from panels.htmls.html_config import *
from panels.new_customer import New_Customer

if __name__[:10] == "bokeh_app_":
    NC = New_Customer(ini_section="local_stability")


    # Survey=column(row(survey_desc,
    #                 column(*Customer_Inputs,width=320)),
    #               row(inputs1,inputs2)
    #               )
    # #
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
