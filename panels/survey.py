from collections import OrderedDict
from functools import partial

from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Div, Select, Slider, TextInput,Panel, Tabs,Button, RangeSlider

from panels.psql.db_admin import DBAdmin
from panels.htmls.html_config import div_html
from panels.psql.bokeh import DBInfo

class Survey(DBInfo):
    survey_options=[str(i) for i in range(1,6)]
    income_options=[str(i) for i in range(0,50000,3000)]
    def __init__(self,*args,**kwargs):
        DBInfo.__init__(self,ini_section = kwargs['ini_section'])
        self.aurvey_fields()

    def aurvey_fields(self):
        survey_fields=f"""
        select column_name
        from information_schema.columns
        where table_schema in ('{self.schema}')
        and table_name in ('survey')
        and column_name not in {repr(DBAdmin.non_survey_columns)}
        order by ordinal_position;
        """
        self.Selects=OrderedDict()
        for column in self.fetchall(survey_fields):
            self.select_fields(column[0])
    def select_fields(self,sfield):
        fields = self.get_all_options()
        if sfield != 'income':
            select=Select(title=sfield,value='3',options=self.survey_options)
        else:
            select=Select(title=sfield,value='12000',options=self.income_options)
        button = Button(label=sfield+' on')
        self.Selects[button]=select
        button.on_click(partial(self.govern_visibility,button=button))
        return self
    def get_all_options(self):
        return self.survey_options

    def desc(self):
        return div_html("survey.html",sizing_mode="stretch_width")
    def govern_visibility(self,button):
        #for button in self.Sliders.keys():
        if button.label[-2:]=='on':
            button.label=button.label[:-2]+'off'
            self.Selects[button].visible=False
        else:
            button.label=button.label[:-3]+'on'
            self.Selects[button].visible=True
    def submit(self,label="submit survey"):
        self.ins_survey_button=Button(label=label, button_type="success")
        self.ins_survey_button.on_click(self.ins_survey)
        return self.ins_survey_button
    def ins_survey(self):
        ins_str=\
        """
        INSERT INTO
        survey({},
            time,
            notes,score,
            customer_id)
        VALUES({},
            NOW(),
            %s,%s,
            (
            SELECT customer_id
            FROM customers
            WHERE customers.name=%s
            )
        );
        """
        str_inputs,values=self.insert_inputs()
        self.insertToDB(ins_str.format(*str_inputs),*values)
        self.reset_survey()
    def insert_inputs(self):
        columns=[]
        values=[]
        for button in self.Selects:
            if button.label[-2:]=='on':
                columns.append(self.Selects[button].title)
                values.append(self.Selects[button].value)
        if len(self.survey_notes.value) == 0:
            values+=[None]
        else:
            values+=[self.survey_notes.value]
        values+=[str(self.custo_score.value),
                self.cust_dropdown.value]
        values_ph=('%s,'*len(columns))[:-1]
        cols=','.join(columns)
        return (cols,values_ph,), values
    def reset_survey(self):
        for button in self.Selects:
            self.Selects[button].value='3'
        self.cust_dropdown.value='None'
        self.cust_dropdown.options=['None']
        self.cust_notes_update()

    def cust_score(self):
        self.custo_score=Slider(title='Customer Score', start=0, end=9, value=3, step=1)
        return self.custo_score
    def get_cust_score(self):
        score = self.fetchone("SELECT score FROM customers WHERE name = %s;",
                                self.cust_dropdown.value)
        if score[0]:
            return div_html("notes.html",args=('Customer',notes[0],))
        else:
            return div_html("notes.html",args=('Customer','',))
    def new_survey_notes(self):
        self.survey_notes=TextInput(title="Survey Notes:")
        return self.survey_notes
