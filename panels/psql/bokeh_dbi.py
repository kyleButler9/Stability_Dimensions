
from typing import Text
from bokeh.models import Select, TextInput,Div
from bokeh.events import MenuItemClick

from panels.psql.config import *
from panels.psql.db_admin import *
from panels.htmls.html_config import init_notes_div,format_notes

class HierarchicalFields(DBI):
    cname="None"
    gname="''"
    def class_name_contains(self):
        self.downsample_classes=TextInput(title="class name contains:")
        self.downsample_classes.on_change('value', lambda attr, old, new: self.downsample_class_handler(new.strip()))
        return self.downsample_classes
    def class_dd(self):
        self.classes = self.get_10_classes()
        self.class_dropdown=Select(title="class",
                value=self.gname,
                options=self.classes)
        self.class_dropdown.on_change('value',lambda attr, old, new: self.class_selected(new))
        return self.class_dropdown
    def cust_dd(self):
        self.custs = self.get_10_customers()
        self.cust_dropdown=Select(title="Customers",
                value=self.cname,
                options=self.custs)
        self.cust_dropdown.on_change('value',lambda attr, old, new: self.customer_selected(new))
        return self.cust_dropdown
    
    def get_10_classes(self):
        try:
            class_name_substr=self.downsample_classes.value.strip()
        except AttributeError:
            class_name_substr="''"
        classes = self.fetchall("SELECT name FROM classes WHERE name ~* %s limit 10;",class_name_substr)
        if len(classes) == 1:
            self.class_selected(classes[0][0])
        elif len(classes) > 1:
            self.class_selected("''")
        else:
            print('no class name selected with \nclass name substr:',class_name_substr)
        return [c[0] for c in classes]
    def get_10_customers(self):
        try:
            cust_name_substr=self.downsample_cust.value.strip()
        except AttributeError:
            cust_name_substr="''"
        customers = self.fetchall("""
            SELECT c.name
            FROM customers c
            JOIN classes USING (class)
            LEFT OUTER JOIN survey USING (customer_id)
            WHERE c.name ~* %s
            AND classes.name ~* %s
            order by survey.time desc
            limit 10;
            """,
            cust_name_substr,
            self.gname)
        if len(customers) == 1:
            self.customer_selected(customers[0][0])
        elif len(customers) > 1:
            self.customer_selected("None")
        else:
            print('no customer selected with \nname substr:',cust_name_substr,'\n class substr:',self.gname)
        return [customer[0] for customer in customers]
    def class_selected(self,gname):
        self.gname=gname
        self.class_notes_update()
        try:
            cust_substr=self.downsample_cust.value
        except AttributeError:
            cust_substr="''"
        self.downsample_cust_handler(cust_substr)
    def customer_selected(self,cname):
        self.cname=cname
        self.cust_notes_update()
    def cust_name_contains(self):
        self.downsample_cust=TextInput(title="Customer name contains:")
        self.downsample_cust.on_change('value', lambda attr, old, new: self.downsample_cust_handler(new.strip()))
        return self.downsample_cust
    def downsample_class_handler(self,substr):
        classes = self.fetchall("SELECT name FROM classes WHERE name ~* %s;",substr)
        if len(classes) == 1:
            self.class_selected(classes[0][0])
        elif len(classes) > 1:
            self.class_selected("''")
        else:
            print('FLAG: no class selected for \nclass name substr:',substr)
            classes=[('None',)]
        self.class_dropdown.options=[c[0] for c in classes]
    def downsample_cust_handler(self,substr):
        customers = self.fetchall("""
            SELECT customers.name
            FROM customers
            JOIN classes USING (class)
            WHERE customers.name ~* %s
            AND classes.name ~* %s;
            """,
            substr,
            self.gname)
        if len(customers) == 1:
            self.customer_selected(customers[0][0])
        elif len(customers) > 1:
            self.customer_selected("None")
        else:
            print('no customer selected with \nname substr:',substr,'\n class substr:',self.gname)
        try:
            self.cust_dropdown.options=[customer[0] for customer in customers]
        except AttributeError:
            self.cust_dd().options=[customer[0] for customer in customers]
    def class_notes(self):
        notes=self.fetchone("SELECT COALESCE(notes,' ') FROM classes WHERE name = %s",self.gname)
        if not notes:
            print("FLAG: no class notes for class:",self.gname)
            notes=('',)
        self.class_notes_div=init_notes_div('class',notes[0])
        return self.class_notes_div
    def cust_notes(self):
        notes=self.fetchone("""
            SELECT COALESCE(customers.notes,' ') 
            FROM customers
            JOIN classes USING (class)
            WHERE customers.name ~* %s
            AND classes.name ~* %s;
            """,
            self.cname,
            self.class_name)
        if not notes:
            print('FLAG: no cust notes for \ncust:',self.cname,'\nclass:',self.class_name)
            notes=('',)
        self.cust_notes_=init_notes_div('Customer',notes[0])
        return self.cust_notes_
    def class_notes_update(self):
        # updates (or initializes then updates) class notes
        notes=self.fetchone("SELECT COALESCE(notes,' ') FROM classes WHERE name = %s",self.gname)
        formatted_notes=format_notes('class',notes[0])
        try:
            self.class_notes_div.text=formatted_notes
        except AttributeError:
            self.class_notes().text=formatted_notes
    def cust_notes_update(self):
        # updates (or initializes then updates) customer notes
        notes=self.fetchone("""
            SELECT COALESCE(customers.notes,' ') 
            FROM customers
            JOIN classes USING (class)
            WHERE customers.name ~* %s
            AND classes.name ~* %s;
            """,
            self.cname,
            self.gname)
        formatted_notes=format_notes('Customer',notes[0])
        try:
            self.cust_notes_.text=formatted_notes
        except AttributeError:
            nf = self.cust_notes()
            if type(nf) == Div:
                nf.text=formatted_notes
            elif type(nf) == TextInput:
                nf.value=formatted_notes