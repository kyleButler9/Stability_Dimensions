from bokeh.layouts import column, row
from bokeh.models import Select, TextInput,Button

from panels.psql.config import *
from panels.htmls.html_config import *
from panels.psql.bokeh_dbi import *


# this class needs to make use of VarcharDBI like Survey and Export Csv do
class New_Customer(VarcharDBI):
    def __init__(self,*args,**kwargs):
        VarcharDBI.__init__(self,ini_section=kwargs['ini_section'])
    def cust_name(self):
        self.cust_name_=TextInput(title="Name")
        return self.cust_name_
    def cust_address(self):
        self.cust_address_=TextInput(title="Address")
        return self.cust_address_
    def cust_notes(self):
        self.cust_notes_ =TextInput(title="Notes")
        return self.cust_notes_
    def cust_button(self):
        self.cust_button_ = Button(label="Add New Customer", button_type="success")
        self.cust_button_.on_click(self.ins_cust_handler)
        return self.cust_button_
    def ins_cust_handler(self):
        doNothing=False
        print('ins cust0')
        if len(self.cust_name_.value) == 0:
            doNothing=True
        if len(self.cust_address_.value) == 0 and len(self.cust_notes_.value) == 0:
            new_cust = \
            """
            DROP TABLE IF EXISTS user_inputs;
            CREATE TEMP TABLE user_inputs(
                name VARCHAR(255),
                group_id INTEGER
                );
            INSERT INTO user_inputs(
                name,
                group_id
            )
            VALUES (
                %s,
                (SELECT group_id
                FROM groups
                WHERE groups.name = %s)
            );
            INSERT into customers(name,group_id)
            VALUES (%s,
                SELECT group_id
                FROM groups
                WHERE groups.name = %s)
            ON CONFLICT (name) DO UPDATE
                SET group_id = EXCLUDED.group_id
            RETURNING customer_id as customer;
            """
            self.insertToDB(new_cust,
                self.cust_name_.value,
                self.group_dropdown.value)
        elif len(self.cust_address_.value) == 0:
            new_cust = \
            """
            DROP TABLE IF EXISTS user_inputs;
            CREATE TEMP TABLE user_inputs(
                name VARCHAR(255),
                notes VARCHAR(255),
                group_id INTEGER
                );
            INSERT INTO user_inputs(
                name,
                notes,
                group_id
            )
            VALUES (
                %s,
                %s,
                (SELECT group_id
                FROM groups
                WHERE groups.name = %s)
            );
            INSERT INTO customers(name,notes,group_id)
                SELECT name,notes,group_id
                    FROM user_inputs
            ON CONFLICT (name) DO UPDATE
                SET notes = EXCLUDED.notes,
                    group_id = EXCLUDED.group_id
            RETURNING customer_id as customer;
            """
            self.insertToDB(new_cust,
                self.cust_name_.value,
                self.cust_notes_.value,
                self.group_dropdown.value)
        elif len(self.cust_notes_.value) == 0:
            new_cust = \
            """
            DROP TABLE IF EXISTS user_inputs;
            CREATE TEMP TABLE user_inputs(
                name VARCHAR(255),
                address VARCHAR(255),
                group_id INTEGER
                );
            INSERT INTO user_inputs(
                name,
                address,
                group_id
            )
            VALUES (
                %s,
                %s,
                (SELECT group_id
                FROM groups
                WHERE groups.name = %s)
            );
            INSERT INTO customers(name,address,group_id)
                SELECT name,address,group_id
                    FROM user_inputs
            ON CONFLICT (name) DO UPDATE
                SET address = EXCLUDED.address,
                    group_id = EXCLUDED.group_id
            RETURNING customer_id as customer;
            """
            self.insertToDB(new_cust,
                self.cust_name_.value,
                self.cust_address_.value,
                self.group_dropdown.value)
        else:
            new_cust = \
            """
            DROP TABLE IF EXISTS user_inputs;
            CREATE TEMP TABLE user_inputs(
                name VARCHAR(255),
                address VARCHAR(255),
                notes VARCHAR(255),
                group_id INTEGER
                );
            INSERT INTO user_inputs(
                name,
                address,
                notes,
                group_id
            )
            VALUES (
                %s,
                %s,
                %s,
                (SELECT group_id
                FROM groups
                WHERE groups.name = %s)
            );
            INSERT INTO customers(name,address,notes,group_id)
                SELECT name,address,notes,group_id
                    FROM user_inputs
            ON CONFLICT (name) DO UPDATE
                SET address = EXCLUDED.address,
                    group_id = EXCLUDED.group_id,
                    notes = EXCLUDED.notes
            RETURNING customer_id as customer;
            """
            self.insertToDB(new_cust,
                self.cust_name_.value,
                self.cust_address_.value,
                self.cust_notes_.value,
                self.group_dropdown.value)
        if not doNothing:
            self.clear_cust_info()
    def clear_cust_info(self):
        self.cust_name_.value=""
        self.cust_address_.value=""
        self.cust_notes_.value=""
        return self
    def desc(self):
        return div_html("new_customer_banner.html",sizing_mode="stretch_width")
    def new_group_name_input(self):
        self.new_group_name=TextInput(title="New Group:")
        return self.new_group_name
    def new_group_notes_input(self):
        self.new_group_notes=TextInput(title="Group Notes:")
        return self.new_group_notes
    def insert_new_group_button(self,label="Add New Group"):
        self.ins_group=Button(label=label, button_type="success")
        self.ins_group.on_click(self.ins_group_handler)
        return self.ins_group
    def ins_group_handler(self,event):
        gname=self.new_group.value
        gnotes=self.group_notes_input.value
        if len(gnotes) == 0:
            new_group="""
            INSERT INTO groups(name) VALUES(%s)
            ON CONFLICT (name) DO UPDATE 
                SET notes = groups.notes
            RETURNING group_id as group;
            """
            self.insertToDB(new_group,gname)
        else:
            new_group = \
            """
            DROP TABLE IF EXISTS user_inputs;
            CREATE TEMP TABLE user_inputs(
                name VARCHAR(255),
                notes VARCHAR(255)
                );
            INSERT INTO user_inputs(
                name,
                notes
    	    )
            VALUES (
                %s,
                %s
            );
            INSERT INTO groups(name,notes)
                SELECT name,notes
                    FROM user_inputs
            ON CONFLICT (name) DO UPDATE
                SET notes = EXCLUDED.notes
            RETURNING group_id as group
            """
            self.insertToDB(new_group,gname,gnotes)

        self.downsample_group_handler()
        self.new_group_name.value=""
        self.new_group_notes.value=""
