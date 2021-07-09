
from bokeh.models import (Button, ColumnDataSource, CustomJS, DataTable,
                          NumberFormatter, RangeSlider, TableColumn)
from panels.psql.config import *
from panels.htmls.html_config import div_html
from panels.psql.bokeh import DBInfo

from os.path import dirname, join

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

    def update():

        get_cols = \
        f"""
        SELECT  c.name,g.name, {','.join(self.fields.keys())}
        FROM survey
        JOIN customers c USING (customer_id)
        JOIN groups g USING (group_id)
        """
        params = tuple()
        first = True
        if self.nameFilter.index("end") != 0:
            if first is False:
                sqlStr += 'AND g.name = %s '
            else:
                sqlStr += ' WHERE g.name = %s '
                first = False
            params+= (self.nameFilter.get(),)
        if self.nameFilter.index("end") != 0:
            if first is False:
                sqlStr += 'AND c.name = %s '
            else:
                sqlStr += ' WHERE c.name = %s '
                first = False
            params+= (self.nameFilter.get(),)
        current = df[(df['salary'] >= slider.value[0]) & (df['salary'] <= slider.value[1])].dropna()
        source.data = {
            'name'             : current.name,
            'salary'           : current.salary,
            'years_experience' : current.years_experience,
        }
    def set_button(self):
        button = Button(label="Download", button_type="success")
        button.js_on_click(CustomJS(args=dict(source=self.source),
                                    code=open(join(dirname(__file__), "js/download.js")).read()))
        return button
    def set_datatable(self):
        self.data_table = DataTable(source=self.source, columns=self.columns, width=800)
        return self.data_table


slider = RangeSlider(title="Max Salary", start=10000, end=110000, value=(10000, 50000), step=1000, format="0,0")
slider.on_change('value', lambda attr, old, new: update())

#controls = column(slider, button)

#curdoc().add_root(row(controls, data_table))