from collections import OrderedDict
from functools import partial

from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Div, Select, Slider, TextInput,Panel, Tabs,Button, RangeSlider

from panels.psql.db_admin import DBAdmin
from panels.htmls.html_config import init_notes_div,div_html
from panels.psql.bokeh_dbi import VarcharDBI

class Survey(VarcharDBI):
    survey_options=[str(i) for i in range(1,6)]
    income_options=[str(i) for i in range(0,50000,3000)]
    def __init__(self,*args,**kwargs):
        VarcharDBI.__init__(self,ini_section = kwargs['ini_section'])
        self.Selects=self.survey_fields()

    def survey_fields(self):
        survey_fields=f"""
        select column_name
        from information_schema.columns
        where table_schema in ('{self.schema}')
        and table_name in ('survey')
        and column_name not in {DBAdmin.non_survey_columns.string_repr()}
        order by ordinal_position;
        """
        fields = self.fetchall(survey_fields)
        button_selects=[
            (
                Button(title='income on'),
                Select(title='income',value='12000',options=self.income_options)
            )
        ]
        for col in list(set(fields) - set(('income',))):
            button_selects.append(
                (
                    Button(label=col[0]+' on'),
                    Select(title=col[0],value='3',options=self.survey_options)
                )
            )
        for butn in button_selects:
            butn.on_click(partial(self.govern_visibility,button=butn))
        return OrderedDict(button_selects)

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
        return self
    def submit(self,label="submit survey"):
        ins_survey_button=Button(label=label, button_type="success")
        ins_survey_button.on_click(self.ins_survey)
        return ins_survey_button
    def ins_survey(self):
        ins_str=\
        """
        INSERT INTO
        survey({},
            time
            )
        VALUES({}
            (
            SELECT customer_id
            FROM customers
            WHERE customers.name=%s
            ),
            NOW()
        );
        """
        str_inputs,values=self.insert_inputs()
        self.insertToDB(ins_str.format(*str_inputs),*values)
        self.reset_survey()
        return self
    def insert_inputs(self):
        entries = []
        for button in self.Selects:
            if button.label[-2:]=='on':
                entries.append(
                    (
                        self.Selects[button].title,
                        self.Selects[button].value
                    )
                )
        if len(self.survey_notes.value) != 0:
            entries.append(
                (
                    'notes',
                    self.survey_notes.value
                )
            )
        entries+=[
            (
                'score',
                str(self.custo_score.value)
            ),
            (
                'customer_id',
                self.cust_dropdown.value
            )
        ]
        _entries=list(zip(*entries))
        values_ph='%s,'*(len(entries)-1)
        cols=','.join(_entries[0])
        return (cols,values_ph,), _entries[1]
    def reset_survey(self):
        for button in self.Selects:
            if button.label[:6] != 'income':
                self.Selects[button].value='3'
            else:
                self.Selects[button].value='12000'
        self.cust_dropdown.value='None'
        self.cust_dropdown.options=['None']
        self.cust_notes_update()
        return self
    def cust_score(self):
        self.custo_score=Slider(title='Customer Score', start=0, end=9, value=3, step=1)
        return self.custo_score
    def get_cust_score(self):
        score = self.fetchone("SELECT COALESCE(score,' ') FROM customers WHERE name = %s;",
                                self.cust_dropdown.value)
        if score:
            _score=score[0]
        else:
            _score=''
        return init_notes_div('Customer',_score,)
    def new_survey_notes(self):
        self.survey_notes=TextInput(title="Survey Notes:")
        return self.survey_notes
        # self.Selects=OrderedDict((Button(label=f[0]+' on'),
        #             Select(title=sfield,value='3',options=self.survey_options)) 
        #             for f in fields if f[0] != 'income' 
        #             else 
        #             (Button(label=f[0]+' on'),
        #             Select(title=sfield,value='3',options=self.survey_options)) )
        # _kwargs=dict((k,kwargs[k]) for k in kwargs if k != 'args')

    #     for column in self.fetchall(survey_fields):
    #         self.select_fields(column[0])
    # def select_fields(self,sfield):
    #     if sfield != 'income':
    #         select=Select(title=sfield,value='3',options=self.survey_options)
    #     else:
    #         select=Select(title=sfield,value='12000',options=self.income_options)
    #     button = Button(label=sfield+' on')
    #     self.Selects[button]=select
    #     button.on_click(partial(self.govern_visibility,button=button))
    #     return self