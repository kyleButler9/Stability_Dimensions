from os.path import dirname, join
from collections import OrderedDict

from panels.psql.config import *
from panels.htmls.html_config import div_html
from panels.psql.bokeh import DBInfo
from panels.psql.db_admin import DBAdmin

from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import (Button, ColumnDataSource, CustomJS, DataTable,
                          NumberFormatter, RangeSlider, TableColumn)

class Export_Csv(DBInfo):
    def __init__(self,*args,**kwargs):
        DBInfo.__init__(self,ini_section = kwargs['ini_section'])
        survey_fields=f"""
        select column_name
        from information_schema.columns
        where table_schema in ('{self.schema}')
        and table_name in ('survey')
        and column_name not in {repr(DBAdmin.non_survey_columns)}
        order by ordinal_position;
        """
        self.fields=OrderedDict()
        self.data=dict()
        for field in self.fetchall(survey_fields):
            field = field[0]
            #consider axis map for title
            self.fields[field]=TableColumn(field=field, title=field)
            self.data[field]=[]
        self.source=ColumnDataSource(data=self.data)
    def desc(self):
        return div_html("export_csv.html",sizing_mode="stretch_width")
    def update(self):
        get_vals = \
        f"""
        SELECT  c.name,g.name, {','.join(self.fields.keys())}
        FROM survey
        JOIN customers c USING (customer_id)
        LEFT OUTER JOIN groups g USING (group_id)
        """
        params = []
        first = True
        if self.group_dropdown.value != 'None':
            if first is False:
                get_vals += 'AND g.name = %s '
            else:
                get_vals += ' WHERE g.name = %s '
                first = False
            params.append(self.group_dropdown.value)
        if self.cust_dropdown.value != 'None':
            if first is False:
                get_vals += 'AND c.name = %s '
            else:
                get_vals += ' WHERE c.name = %s '
                first = False
            params.append(self.cust_dropdown.value)
        data = self.fetchall(get_vals+';',*params)
        d = dict(c_name=[],g_name=[])
        for key in self.fields.keys():
            d[key]=[]
        for dat in data:
            d['c_name'].append(dat[0])
            d['g_name'].append(dat[1])
            i=2
            for key in self.fields.keys():
                d[key].append(dat[i])
                i+=1
        self.source.data = d
    def set_button(self):
        button = Button(label="Download", button_type="success")
        button.js_on_click(CustomJS(args=dict(source=self.source),
                                    code=open(join(dirname(__file__), "js/download.js")).read()))
        return button
    def set_datatable(self):
        self.data_table = DataTable(source=self.source, columns=[self.fields[field] for field in self.fields.keys()], width=800)
        return self.data_table
    def group_notes_update(self):
        self.update()
        self.downsample_cust_handler()
        notes=self.fetchone("SELECT COALESCE(notes,'') FROM groups WHERE name = %s",
                                self.group_dropdown.value)
        if notes:
            self.group_markup.text=div_html("notes.html",args=('Group',notes[0],)).text
        else:
            self.group_markup.text = div_html("notes.html",args=('Group','',)).text
    def cust_notes_update(self):
        self.update()
        notes=self.fetchone("SELECT COALESCE(notes,'') FROM customers WHERE name = %s",
                                self.cust_dropdown.value)
        if notes:
            self.cust_markup.text=div_html("notes.html",args=('Customer',notes[0],)).text
        else:
            self.cust_markup.text = div_html("notes.html",args=('Customer','',)).text
