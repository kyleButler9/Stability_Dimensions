
from bokeh.models import Select, TextInput
from bokeh.events import MenuItemClick

from panels.psql.config import *
from panels.psql.db_admin import *
from panels.htmls.html_config import *

# VarcharDBI
# eventually this class will just have a general Select, Slider
class VarcharDBI(DBI):
    cname="None"
    gname="None"
    def group_name_contains(self):
        self.downsample_groups=TextInput(title="Group name contains:")
        self.downsample_groups.on_change('value', lambda attr, old, new: self.downsample_group_handler(new.strip()))
        return self.downsample_groups
    def group_dd(self):
        self.groups = self.get_all_groups()
        self.group_dropdown=Select(title="Group",
                value=self.gname,
                options=self.groups)
        self.group_dropdown.on_change('value',lambda attr, old, new: self.group_selected(new))
        return self.group_dropdown
    def cust_dd(self):
        self.custs = self.get_10_customers()
        self.cust_dropdown=Select(title="Customers",
                value=self.cname,
                options=self.custs)
        self.cust_dropdown.on_change('value',lambda attr, old, new: self.customer_selected(new))
        return self.cust_dropdown
    def group_notes(self):
        notes=self.fetchone("SELECT COALESCE(notes,'') FROM groups WHERE name = %s",self.gname)
        if notes:
            self.group_markup=div_html("notes.html",args=('Group',notes[0],))
        else:
            self.group_markup = div_html("notes.html",args=('Group','',))
        return self.group_markup
    def cust_notes(self):
        notes=self.fetchone("SELECT COALESCE(notes,'') FROM customers WHERE name = %s",self.cname)
        if notes:
            self.cust_markup=div_html("notes.html",args=('Customer',notes[0],))
        else:
            self.cust_markup = div_html("notes.html",args=('Customer','',))
        return self.cust_markup
    def cust_notes_update(self):
        notes=self.fetchone("SELECT COALESCE(notes,'') FROM customers WHERE name = %s",self.cname)
        try:
            self.cust_markup.text=self.notes_to_div('Customer',notes)
        except AttributeError:
            self.cust_notes()
            self.cust_markup.text=self.notes_to_div('Customer',notes)
    def group_selected(self,gname):
        self.gname=gname
        try:
            self.group_notes_update()
        except AttributeError:
            self.group_notes()
            self.group_notes_update()
        try:
            self.downsample_cust_handler(self.downsample_cust.value)
        except AttributeError:
            self.cust_name_contains()
            self.downsample_cust_handler(self.downsample_cust.value)
    def group_notes_update(self):
        notes=self.fetchone("SELECT COALESCE(notes,'') FROM groups WHERE name = %s",self.gname)
        try:
            self.group_markup.text=self.notes_to_div('Group',notes)
        except AttributeError:
            self.group_notes()
            self.group_markup.text=self.notes_to_div('Group',notes)
    def notes_to_div(self,cat,notes):
        if notes:
            return div_html("notes.html",args=(cat,notes[0],)).text
        else:
            return div_html("notes.html",args=(cat,'',)).text
    def downsample_group_handler(self,substr):
        groups = self.fetchall("SELECT name FROM groups WHERE name ~* %s;",substr)
        if len(groups) == 1:
            self.group_selected(groups[0][0])
        elif len(groups) > 1:
            self.group_selected("None")
        self.group_dropdown.options=[group[0] for group in groups]
    def get_all_groups(self):
        groups = self.fetchall("SELECT name FROM groups;")
        if len(groups) == 1:
            self.group_selected(groups[0][0])
        elif len(groups) > 1:
            self.group_selected("None")
        return [group[0] for group in groups]
    def get_10_customers(self):
        customers = self.fetchall("""
            SELECT c.name
            FROM customers c
            JOIN groups USING (group_id)
            LEFT OUTER JOIN survey USING (customer_id)
            WHERE c.name ~* %s
            AND groups.name = %s
            order by survey.time desc
            limit 10;
            """,
            self.downsample_cust.value.strip(),
            self.gname)
        if len(customers) == 1:
            self.customer_selected(customers[0][0])
        elif len(customers) > 1:
            self.customer_selected("None")
        return [customer[0] for customer in customers]
    def customer_selected(self,cname):
        self.cname=cname
        try:
            self.cust_notes_update()
        except AttributeError:
            self.cust_notes()
            self.cust_notes_update()
    def cust_name_contains(self):
        self.downsample_cust=TextInput(title="Customer name contains:")
        self.downsample_cust.on_change('value', lambda attr, old, new: self.downsample_cust_handler(new.strip()))
        return self.downsample_cust
    def downsample_cust_handler(self,substr):
        customers = self.fetchall("""
            SELECT customers.name
            FROM customers
            JOIN groups USING (group_id)
            WHERE customers.name ~* %s
            AND groups.name = %s;
            """,
            substr,
            self.gname)
        if len(customers) == 1:
            self.customer_selected(customers[0][0])
        elif len(customers) > 1:
            self.customer_selected("None")
        try:
            self.cust_dropdown.options=[customer[0] for customer in customers]
        except AttributeError:
            self.cust_dd()
            self.cust_dropdown.options=[customer[0] for customer in customers]
