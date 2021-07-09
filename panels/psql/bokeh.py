
from bokeh.models import Select, TextInput

from panels.psql.config import *
from panels.psql.db_admin import *
from panels.htmls.html_config import *

class DBInfo(DBI):
    def group_name_contains(self):
        self.downsample_groups=TextInput(title="Group name contains:")
        self.downsample_groups.on_change('value', lambda attr, old, new: self.downsample_group_handler())
        return self.downsample_groups
    def group_dd(self):
        groups = self.get_all_groups()
        self.group_dropdown=Select(title="Group",
                value="None",
                options=groups)
        self.group_dropdown.on_change('value',lambda attr, old, new: self.group_notes_update())
        return self.group_dropdown
    def cust_dd(self):
        custs = self.get_10_customers()

        self.cust_dropdown=Select(title="Customers",
                value="None",
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
        self.downsample_cust_handler()
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
