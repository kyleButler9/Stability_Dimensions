
from bokeh.models import Select, TextInput
from bokeh.events import MenuItemClick

from panels.psql.config import *
from panels.psql.db_admin import *
from panels.htmls.html_config import init_notes_div,format_notes

class VarcharDBI(DBI):
    cname="None"
    gname="''"
    def group_name_contains(self):
        self.downsample_groups=TextInput(title="Group name contains:")
        self.downsample_groups.on_change('value', lambda attr, old, new: self.downsample_group_handler(new.strip()))
        return self.downsample_groups
    def group_dd(self):
        self.groups = self.get_10_groups()
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
    
    def get_10_groups(self):
        try:
            group_name_substr=self.downsample_groups.value.strip()
        except AttributeError:
            group_name_substr="''"
        groups = self.fetchall("SELECT name FROM groups WHERE name ~* %s limit 10;",group_name_substr)
        if len(groups) == 1:
            self.group_selected(groups[0][0])
        elif len(groups) > 1:
            self.group_selected("''")
        else:
            print('no group name selected with \ngroup name substr:',group_name_substr)
        return [group[0] for group in groups]
    def get_10_customers(self):
        try:
            cust_name_substr=self.downsample_cust.value.strip()
        except AttributeError:
            cust_name_substr="''"
        customers = self.fetchall("""
            SELECT c.name
            FROM customers c
            JOIN groups USING (group_id)
            LEFT OUTER JOIN survey USING (customer_id)
            WHERE c.name ~* %s
            AND groups.name ~* %s
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
            print('no customer selected with \nname substr:',cust_name_substr,'\n group substr:',self.gname)
        return [customer[0] for customer in customers]
    def group_selected(self,gname):
        self.gname=gname
        self.group_notes_update()
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
    def downsample_group_handler(self,substr):
        groups = self.fetchall("SELECT name FROM groups WHERE name ~* %s;",substr)
        if len(groups) == 1:
            self.group_selected(groups[0][0])
        elif len(groups) > 1:
            self.group_selected("''")
        else:
            print('FLAG: no group selected for \ngroup name substr:',substr)
            groups=[('None',)]
        self.group_dropdown.options=[group[0] for group in groups]
    def downsample_cust_handler(self,substr):
        customers = self.fetchall("""
            SELECT customers.name
            FROM customers
            JOIN groups USING (group_id)
            WHERE customers.name ~* %s
            AND groups.name ~* %s;
            """,
            substr,
            self.gname)
        if len(customers) == 1:
            self.customer_selected(customers[0][0])
        elif len(customers) > 1:
            self.customer_selected("None")
        else:
            print('no customer selected with \nname substr:',substr,'\n group substr:',self.gname)
        try:
            self.cust_dropdown.options=[customer[0] for customer in customers]
        except AttributeError:
            self.cust_dd().options=[customer[0] for customer in customers]
    def group_notes(self):
        notes=self.fetchone("SELECT COALESCE(notes,' ') FROM groups WHERE name = %s",self.gname)
        if not notes:
            print("FLAG: no group notes for group:",self.gname)
            notes=('',)
        self.group_notes_div=init_notes_div('Group',notes[0])
        return self.group_notes_div
    def cust_notes(self):
        notes=self.fetchone("""
            SELECT COALESCE(customers.notes,' ') 
            FROM customers
            JOIN groups USING (group_id)
            WHERE customers.name ~* %s
            AND groups.name ~* %s;
            """,
            self.cname,
            self.gname)
        if not notes:
            print('FLAG: no cust notes for \ncust:',self.cname,'\ngroup:',self.gname)
            notes=('',)
        self.cust_notes_div=init_notes_div('Customer',notes[0])
        return self.cust_notes_div
    def group_notes_update(self):
        # updates (or initializes then updates) group notes
        notes=self.fetchone("SELECT COALESCE(notes,' ') FROM groups WHERE name = %s",self.gname)
        formatted_notes=format_notes('Group',notes[0])
        try:
            self.group_notes_div.text=formatted_notes
        except AttributeError:
            self.group_notes().text=formatted_notes
    def cust_notes_update(self):
        # updates (or initializes then updates) customer notes
        notes=self.fetchone("""
            SELECT COALESCE(customers.notes,' ') 
            FROM customers
            JOIN groups USING (group_id)
            WHERE customers.name ~* %s
            AND groups.name ~* %s;
            """,
            self.cname,
            self.gname)
        formatted_notes=format_notes('Customer',notes[0])
        try:
            self.cust_markup.text=formatted_notes
        except AttributeError:
            self.cust_notes().text=formatted_notes