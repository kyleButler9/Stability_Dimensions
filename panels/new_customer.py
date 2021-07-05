from psql.config import *
from bokeh.plotting import show

from os.path import join,dirname

from bokeh.models import ColumnDataSource, Div, Select, Slider, TextInput,Panel, Tabs,Button, RangeSlider

def div_html(html,**kwargs):
    return Div(text=open(join(dirname(__file__), html)).read(),**kwargs)

nc_desc = div_html("htmls/new_customer_banner.html",sizing_mode="stretch_width")


class New_Customer(DBI):
    def __init__(self,*args,**kwargs):
        DBI.__init__(self,ini_section = kwargs['ini_section'])
    def get_groups(self):
        groups = self.fetchall("SELECT name FROM groups;")
        return [group[0] for group in groups]
    def new_customer_panel(self):
        return (nc_desc,
                    row(TextInput(title="Group name contains:"),
                        Select(title="Group",
                                value="All",
                                options=self.get_groups()),
                        Button(label="Add New Group", button_type="success")
                        ),
                    row(TextInput(title="Name"),
                        TextInput(title="Address"),
                        TextInput(title="Notes"),
                        Button(label="Add New Customer", button_type="success")
                        ),
                    )
if __name__ == "__main__":
    from bokeh.models import Panel, Tabs,Button, RangeSlider
    from bokeh.layouts import column, row
    from bokeh.io import curdoc
    y = New_Customer(ini_section="local_stability")
    tab = Panel(child=column(*y.new_customer_panel()),title="Export CSV")
    l=Tabs(tabs=[tab])
    curdoc().add_root(l)
