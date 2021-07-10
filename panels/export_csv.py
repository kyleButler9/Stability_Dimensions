from os.path import dirname, join
from collections import OrderedDict

from panels.htmls.html_config import div_html
from panels.psql.bokeh_dbi import VarcharDBI
from panels.psql.db_admin import DBAdmin

from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import (Button, ColumnDataSource, CustomJS, DataTable,
                          NumberFormatter, RangeSlider, TableColumn)

class Export_Csv(VarcharDBI):
    def __init__(self,*args,**kwargs):
        VarcharDBI.__init__(self,ini_section = kwargs['ini_section'])
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
        columns,d=self.output_data()
        columns=[s.replace('.','_') for s in columns]
        data = dict.fromkeys(columns,[])
        for survey in d[1:]:
            data['c_name'].append(survey[0])
            data['g_name'].append(survey[1])
            i=2
            for key in self.fields.keys():
                data[key].append(survey[i])
                i+=1
        self.source.data = data
    def output_data(self):
        cols = ['c.name','g.name']+list(self.fields.keys())
        get_vals = \
        f"""
        SELECT {','.join(cols)}
        FROM survey
        JOIN customers c USING (customer_id)
        LEFT OUTER JOIN groups g USING (group_id)
        """
        params = []
        first = True
        if self.cname != 'None':
            if first is False:
                get_vals += 'AND c.name = %s '
            else:
                get_vals += ' WHERE c.name = %s '
                first = False
            params.append(self.cust_dropdown.value)
        elif self.gname != 'None':
            if first is False:
                get_vals += 'AND g.name = %s '
            else:
                get_vals += ' WHERE g.name = %s '
                first = False
            params.append(self.group_dropdown.value)
        data=self.fetchall(get_vals+';',*params)
        return cols, data

    def set_button(self):
        button = Button(label="Download", button_type="success")
        button.js_on_click(CustomJS(args=dict(source=self.source),
                                    code=open(join(dirname(__file__), "js/download.js")).read()))
        return button
    def set_datatable(self):
        self.data_table = DataTable(source=self.source, columns=[self.fields[field] for field in self.fields.keys()], width=800)
        return self.data_table
    def group_selected(self,gname):
        self.gname=gname
        self.group_notes_update()
        try:
            self.downsample_cust_handler(self.downsample_cust.value)
        except AttributeError:
            self.cust_name_contains()
            self.downsample_cust_handler(self.downsample_cust.value)
        finally:
            self.update()
    def customer_selected(self,cname):
        self.cname=cname
        self.update()
        self.cust_notes_update()
