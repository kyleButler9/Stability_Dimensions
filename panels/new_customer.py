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
        if len(self.cust_name_.value) == 0:
            return self
        entries =  [
            field for field in [
                ('name',self.cust_name_.value),
                ('address',self.cust_address_.value),
                ('notes',self.cust_notes_.value),
                ('group',self.gname)
            ] if len(field[1])!=0]
        entries=list(zip(*entries))
        if entries[0][0] != 'name' or entries[0][-1]!='group':
            print('no customer name or group provided.')
            return self
        temp_keys=' VARCHAR(255),'.join(entries[0])
        keys=','.join(entries[0])
        vals=','.join(entries[1])
        update_cols=[]
        for key in entries[0]:
            update_cols.append('{0}=EXCLUDED.{0}'.format(key))
        update_cols=','.join([
            col for col in update_cols 
            if col !='name'
            ])
        new_cust =\
        f"""
        DROP TABLE IF EXISTS user_inputs;
        CREATE TEMP TABLE user_inputs({temp_keys});
        INSERT INTO user_inputs({keys})
            VALUES({vals})
        INSERT INTO customers({keys})
            SELECT {keys} FROM user_inputs
            ON CONFLICT (name) DO UPDATE
                SET {update_cols}
        RETURNING customer;
        """
        self.execute_and_commit(new_cust)
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
        gname=str(self.new_group.value)
        gnotes=str(self.group_notes_input.value)
        if len(gname)==0:
            print('provide a group name')
            return self
        if len(gnotes) == 0:
            keys='name'
            vals=gname
            conflict_notes='notes=groups.notes'
        else:
            keys='name,notes'
            vals=','.join(gname,gnotes)
            conflict_notes='notes=EXCLUDED.notes'
        
        new_group=f"""
        INSERT INTO groups({keys}) VALUES({vals})
        ON CONFLICT (name) DO UPDATE 
            SET {conflict_notes}
        RETURNING group_id as group;
        """
        self.execute_and_commit(new_group)
        self.downsample_group_handler(gname)
        self.clear_group_info()
        return self
    def clear_group_info(self):
        self.new_group_name.value=""
        self.new_group_notes.value=""
        return self
