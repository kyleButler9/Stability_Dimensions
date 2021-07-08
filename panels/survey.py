from os.path import join,dirname
from collections import OrderedDict
from functools import partial

from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Div, Select, Slider, TextInput,Panel, Tabs,Button, RangeSlider

from panels.psql.config import *
from panels.psql.db_admin import *
from panels.htmls.html_config import *

class Survey(DBI):
    def __init__(self,*args,**kwargs):
        DBI.__init__(self,ini_section = kwargs['ini_section'])
        survey_fields=f"""
        select column_name
        from information_schema.columns
        where table_schema in ('{self.schema}')
        and table_name in ('survey')
        and column_name not in {repr(DBAdmin.non_survey_columns)}
        order by ordinal_position;
        """
        self.Sliders=OrderedDict()
        for column in self.fetchall(survey_fields):
            slider=Slider(title=column[0], start=0, end=5, value=3, step=1)
            button = Button(label='on')
            self.Sliders[button]=slider
            button.on_click(partial(self.govern_visibility,button=button))
    def govern_visibility(self,button):
        #for button in self.Sliders.keys():
        if button.label=='on':
            button.label='off'
            self.Sliders[button].visible=False
        else:
            button.label='on'
            self.Sliders[button].visible=True
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
        self.insertToDB(ins_str.format(*str_inputs),values)
        self.reset_survey()
    def insert_inputs(self):
        columns=[]
        values=[]
        for button in self.Sliders:
            if button.label=='on':
                columns.append(self.Sliders[button].title)
                values.append(self.Sliders[button].value)

        values+=[self.survey_notes.value,
                self.custo_score.value,
                self.cust_dropdown.value]
        values_ph=('%s,'*len(columns))[:-1]
        cols=','.join(columns)
        return (cols,values_ph,), values
    def reset_survey(self):
        for button in self.Sliders:
            self.Sliders[button].value=3
        self.cust_dropdown.value='None'
        self.cust_dropdown.options=['None']
        self.cust_notes_update()
    def desc(self):
        return div_html("survey.html",sizing_mode="stretch_width")
    def group_name_contains(self):
        self.downsample_groups=TextInput(title="Group name contains:")
        self.downsample_groups.on_change('value', lambda attr, old, new: self.downsample_group_handler())
        return self.downsample_groups
    def group_dd(self):
        groups = self.get_all_groups()
        self.group_dropdown=Select(title="Group",
                value="All",
                options=groups)
        self.group_dropdown.on_change('value',lambda attr, old, new: self.group_notes_update())
        return self.group_dropdown
    def cust_dd(self):
        custs = self.get_10_customers()

        self.cust_dropdown=Select(title="Customers",
                value="All",
                options=custs)
        self.cust_dropdown.on_change('value',lambda attr, old, new: self.cust_notes_update())
        return self.cust_dropdown
    def group_notes(self):
        notes=self.fetchone("SELECT COALESCE(notes,'') FROM groups WHERE name = %s",
                                self.group_dropdown.value)
        if notes:
            self.group_markup=div_html("notes.html",args=('Group',notes[0],))
        else:
            self.group_markup = div_html("notes.html",args=('Group','',))
        return self.group_markup
    def cust_notes(self):
        notes=self.fetchone("SELECT COALESCE(notes,'') FROM customers WHERE name = %s",
                                self.cust_dropdown.value)
        if notes:
            self.cust_markup=div_html("notes.html",args=('Customer',notes[0],))
        else:
            self.cust_markup = div_html("notes.html",args=('Customer','',))
        return self.cust_markup
    def cust_notes_update(self):
        notes=self.fetchone("SELECT COALESCE(notes,'') FROM customers WHERE name = %s",
                                self.cust_dropdown.value)
        if notes:
            self.cust_markup.text=div_html("notes.html",args=('Customer',notes[0],)).text
        else:
            self.cust_markup.text = div_html("notes.html",args=('Customer','',)).text
    def group_notes_update(self):
        notes=self.fetchone("SELECT COALESCE(notes,'') FROM groups WHERE name = %s",
                                self.group_dropdown.value)
        if notes:
            self.group_markup.text=div_html("notes.html",args=('Group',notes[0],)).text
        else:
            self.group_markup.text = div_html("notes.html",args=('Group','',)).text

    def downsample_group_handler(self):
        groups = self.fetchall("SELECT name FROM groups WHERE name ~* %s;",
                                self.downsample_groups.value.strip())
        self.group_dropdown.options=[group[0] for group in groups]
    def get_all_groups(self):
        groups = self.fetchall("SELECT name FROM groups;")
        return [group[0] for group in groups]
    def get_10_customers(self):
        customers = self.fetchall("""
            SELECT customers.name
            FROM customers
            JOIN groups USING (group_id)
            LEFT OUTER JOIN survey USING (customer_id)
            WHERE customers.name ~* %s
            AND groups.name = %s
            order by survey.time desc
            limit 10;
            """,
            self.downsample_cust.value.strip(),
            self.group_dropdown.value)
        return [customer[0] for customer in customers]

    def cust_name_contains(self):
        self.downsample_cust=TextInput(title="Customer name contains:")
        self.downsample_cust.on_change('value', lambda attr, old, new: self.downsample_cust_handler())
        return self.downsample_cust
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
    def cust_notes(self):
        notes=self.fetchone("SELECT COALESCE(notes,'') FROM customers WHERE name = %s",
                                self.cust_dropdown.value)
        if notes:
            self.cust_markup=div_html("notes.html",args=('Customer',notes[0],))
        else:
            self.cust_markup = div_html("notes.html",args=('Customer','',))
        return self.cust_markup
    def cust_notes_update(self):
        notes=self.fetchone("SELECT COALESCE(notes,'') FROM customers WHERE name = %s",
                                self.cust_dropdown.value)
        print(notes)
        if notes:
            self.cust_markup.text=div_html("notes.html",args=('Customer',notes[0],)).text
        else:
            self.cust_markup.text = div_html("notes.html",args=('Customer','',)).text
    def downsample_cust_handler(self):
        customers = self.fetchall("""
            SELECT customers.name
            FROM customers
            JOIN groups USING (group_id)
            WHERE customers.name ~* %s
            AND groups.name = %s;
            """,
            self.downsample_cust.value.strip(),
            self.group_dropdown.value)
        self.cust_dropdown.options=[customer[0] for customer in customers]


# use a table like below to map column names to more readable names
# axis_map = {
#     "Digital Literacy":"literacy",
#     "Income/Living Wage":"income",
#     "Employment Stability":"employability",
#     "Childcare":"childcare",
#     "English Language Skills":"english",
#     "Food Security":"food",
#     "Career Resiliency/Training":"skills",
#     "Education":"education",
#     "Work Clothing":"clothes",
#     "Housing":"housing",
#     "Personal Safety":"safety",
#     "Behavioral Health":"health",
# }
