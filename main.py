from bokeh.models import Panel, Tabs
from bokeh.io import curdoc
from bokeh.layouts import column, row

from panels.new_customer import New_Customer
from panels.survey import Survey

def new_customer_panel(NC):
    panel= (NC.desc(),
            row(NC.group_name_contains(),
                NC.group_dd(),
                NC.group_notes_description()
                ),
            row(NC.cust_name(),
                NC.cust_address(),
                NC.cust_notes(),
                NC.cust_button()
                ),
            row(NC.new_group(),
                NC.new_group_notes(),
                NC.insert_new_group_button()
                ),
            )
    return column(*panel)
def survey_panel(SP):
    panel= (SP.desc(),
            row(SP.group_name_contains(),
                SP.group_dd(),
                SP.group_notes()
                ),
            row(SP.cust_name_contains(),
                SP.cust_dd(),
                SP.cust_notes()
                ),
            )
    for col in SP.Sliders:
        panel += (row(col,SP.Sliders[col]),)

    panel += (row(SP.cust_score(),SP.new_survey_notes()),
            row(SP.submit()),)
    #incl fig here when working
    return column(*panel)

if __name__[:10] == "bokeh_app_":
    ini_section = "local_stability"
    NC = New_Customer(ini_section=ini_section)
    SP = Survey(ini_section=ini_section)

    tab0 = Panel(child=new_customer_panel(NC), title="New Customer")
    tab1 = Panel(child=survey_panel(SP), title="Survey")
    #tab2 = Panel(child=Export_Csv,title="Export CSV")

    l=Tabs(tabs=[tab0,tab1])
    curdoc().add_root(l)
