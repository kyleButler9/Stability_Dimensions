from bokeh.models import Panel, Tabs
from bokeh.io import curdoc
from bokeh.layouts import column, row

from panels.new_customer import New_Customer
from panels.survey import Survey
from panels.export_csv import Export_Csv

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
    panel= [SP.desc(),
            row(SP.group_name_contains(),
                SP.group_dd(),
                SP.group_notes()
                ),
            row(SP.cust_name_contains(),
                SP.cust_dd(),
                SP.cust_notes()
                )]
    i=0
    _row=None
    for select in SP.Selects:
        if i % 3 == 0:
            if _row:
                panel.append(row(*_row))
            _row=[]
        _row.append(SP.Selects[select])
        i+=1
    i=0
    _row=None
    for select in SP.Selects:
        if i % 3 == 0:
            if _row:
                panel.append(row(*_row))
            _row=[]
        _row.append(select)
        i+=1
    panel += [row(SP.cust_score(),SP.new_survey_notes()),
            row(SP.submit())]
    #incl fig here when working
    return column(*panel)
def export_panel(EXP):
    panel= [EXP.desc(),
            row(EXP.group_name_contains(),
                EXP.group_dd(),
                EXP.group_notes()
                ),
            row(EXP.cust_name_contains(),
                EXP.cust_dd(),
                EXP.cust_notes()
                ),
            EXP.set_button()]
    controls = column(*panel)
    return row(controls,EXP.set_datatable())

if __name__[:10] == "bokeh_app_":
    ini_section = "local_stability"
    NC = New_Customer(ini_section=ini_section)
    SP = Survey(ini_section=ini_section)
    EXP = Export_Csv(ini_section=ini_section)

    tab0 = Panel(child=new_customer_panel(NC), title="New Customer")
    tab1 = Panel(child=survey_panel(SP), title="Survey")
    tab2 = Panel(child=export_panel(EXP),title="Export CSV")

    l=Tabs(tabs=[tab0,tab1,tab2])
    curdoc().add_root(l)
