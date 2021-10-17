
from typing import Text
from bokeh.models import Select, TextInput,Div
from bokeh.events import MenuItemClick

from panels.psql.config import *
from panels.psql.db_admin import *
from panels.htmls.html_config import init_notes_div,format_notes

class NameDefaults:
    cust='None_general'
    clas='None_general'
    cat='None'

class HierarchicalFields(DBI):
    an=NameDefaults()
    def cats_dd(self):
        cats = self.get_10_cats()
        self.cats_dropdown=Select(title="Categories",
                value=self.an.cat,
                options=cats)
        self.cats_dropdown.on_change('value',lambda attr, old, new: self.cat_selected(new))
        return self.cats_dropdown
    def class_dd(self):
        classes = self.get_10_classes()
        self.class_dropdown=Select(title="Classes",
                value=self.an.clas,
                options=classes)
        self.class_dropdown.on_change('value',lambda attr, old, new: self.class_selected(new))
        return self.class_dropdown
    def cust_dd(self):
        custs = self.get_10_customers()
        self.cust_dropdown=Select(title="Customers",
                value=self.an.cust,
                options=custs)
        self.cust_dropdown.on_change('value',lambda attr, old, new: self.cust_selected(new))
        return self.cust_dropdown
    
    def get_10_cats(self):
        try:
            name_substr=self.downsample_cat.value.strip()
        except AttributeError:
            name_substr=str()
        results = self.fetchall(f"SELECT name FROM categories WHERE name ~* {name_substr} limit 10;")
        if len(results) == 1:
            self.cat_selected(results[0][0])
        else:
            print('no category name selected with \ncategory name substr:',name_substr)
            results=[(NameDefaults.cat,)]
        return [r[0] for r in results]
    def get_10_classes(self):
        try:
            name_substr=self.downsample_class.value.strip()
        except AttributeError:
            name_substr=str()
        results = self.fetchall("""
            SELECT c.name
            FROM classes c
            JOIN categories g USING (category)
            WHERE c.name ~* %s
            AND g.name ~* %s
            order by c.entrytime desc;
            """,
            name_substr,self.an.cat)
        l=len(results)
        if l >= 1:
            self.class_selected(results[0][0])
        else:
            print('no customer selected with \nname substr:',name_substr,'\n class substr:',self.an.clas)
            results=[(self.an.clas,)]
        return [r[0] for r in results]
    def get_10_customers(self):
        try:
            name_substr=self.downsample_cust.value.strip()
        except AttributeError:
            name_substr=str()
        res = self.fetchall("""
            SELECT c.name
            FROM customers c
            JOIN classes USING (class)
            JOIN categories USING (category)
            WHERE c.name ~* %s
            AND classes.name = %s
            AND customers.name = %s
            order by c.entrytime desc
            limit 10
            ;""",
            name_substr,self.an.clas,self.an.cust)
        if len(res) >= 1:
            self.cust_selected(res[0][0])
        else:
            print('no customer selected with \nname substr:',name_substr,'\n class substr:',self.an.clas)
            res=[(self.an.cust,)]
        return [r[0] for r in res]
    def cat_selected(self,cat):
        self.an.cat=cat
        self.cat_notes_update()
        try:
            classes_substr=self.downsample_class.value
        except AttributeError:
            classes_substr=str()
        self.downsample_class_handler(classes_substr)
    def class_selected(self,clas):
        self.an.clas=clas
        self.class_notes_update()
        try:
            cust_substr=self.downsample_cust.value
        except AttributeError:
            cust_substr=str()
        self.downsample_cust_handler(cust_substr)
    def cust_selected(self,cust):
        self.an.cust=cust
        self.cust_notes_update()
    def cat_name_contains(self):
        self.downsample_cat=TextInput(title="Category name contains:")
        self.downsample_cat.on_change('value', lambda attr, old, new: self.downsample_cat_handler(new.strip()))
        return self.downsample_cat
    def class_name_contains(self):
        self.downsample_class=TextInput(title="Class name contains:")
        self.downsample_class.on_change('value', lambda attr, old, new: self.downsample_class_handler(new.strip()))
        return self.downsample_class
    def cust_name_contains(self):
        self.downsample_cust=TextInput(title="Customer name contains:")
        self.downsample_cust.on_change('value', lambda attr, old, new: self.downsample_cust_handler(new.strip()))
        return self.downsample_cust
    def downsample_cat_handler(self,substr):
        res = self.fetchall("SELECT name FROM categories WHERE name ~* %s;",substr)
        if len(res) >= 1:
            self.cat_selected(res[0][0])
        else:
            print('FLAG: no cat selected for \ncat name substr:',substr)
            res=[(NameDefaults.cat,)]
        options = [r[0] for r in res]
        try:
            self.cats_dropdown.options=options
        except AttributeError:
            self.cats_dd().options=options
    def downsample_class_handler(self,substr):
        res = self.fetchall("""
            SELECT classes.name
            FROM classes
            JOIN categories USING (category)
            WHERE classes.name = %s
            AND categories.name = %s
            ;""",substr,self.an.cat)
        if len(res) >= 1:
            self.class_selected(res[0][0])
        else:
            print('no class selected with \nname substr:',substr,'\n category substr:',self.an.cat)
            res=[(self.an.clas,)]
        options=[r[0] for r in res]
        try:
            self.class_dropdown.options=options
        except AttributeError:
            self.class_dd().options=options
    def downsample_cust_handler(self,substr):
        res = self.fetchall("""
            SELECT customers.name
            FROM customers
            JOIN classes USING (class)
            JOIN categories USING (category)
            WHERE customers.name ~* %s
            AND classes.name = %s
            AND categories.name = %s
            ;""",substr,self.an.clas,self.an.cat)
        if len(res) >= 1:
            self.cust_selected(res[0][0])
        else:
            print('no customer selected with \nname substr:',substr,'\n class substr:',self.an.clas)
            res=[(self.an.cust,)]
        options=[r[0] for r in res]
        try:
            self.cust_dropdown.options=options
        except AttributeError:
            self.cust_dd().options=options
    def cat_notes(self):
        notes=self.fetchone("SELECT COALESCE(notes,' ') FROM categories WHERE name = %s;",self.an.cat)
        if not notes:
            print("FLAG: no cat notes for cat:",self.an.cat)
            notes=('',)
        self.cat_notes_=init_notes_div('Category',notes[0])
        return self.cat_notes_
    def class_notes(self):
        notes=self.fetchone("""
            SELECT COALESCE(customers.notes,' ') 
            FROM classes
            JOIN categories USING (category)
            AND classes.name=%s
            AND categories.name=%s
            ;""",self.an.clas,self.an.cat)
        if not notes:
            print('FLAG: no cust notes for \ncust:',self.an.clas,'\nclass:',self.an.cat)
            notes=('',)
        self.class_notes_=init_notes_div('Class',notes[0])
        return self.class_notes_
    def cust_notes(self):
        notes=self.fetchone("""
            SELECT COALESCE(customers.notes,' ') 
            FROM customers
            JOIN classes USING (class)
            WHERE customers.name ~* %s
            AND classes.name=%s
            AND categories.name=%s
            ;""",self.an.cust,self.an.clas,self.an.cat)
        if not notes:
            print('FLAG: no cust notes for \ncust:',self.an.cust,'\nclass:',self.an.clas)
            notes=('',)
        self.cust_notes_=init_notes_div('Customer',notes[0])
        return self.cust_notes_
    def cat_notes_update(self):
        # updates (or initializes then updates) cat notes
        notes=self.fetchone("SELECT COALESCE(notes,' ') FROM categories WHERE name = %s",self.an.cat)
        formatted_notes=format_notes('category',notes[0])
        try:
            self.cat_notes_.text=formatted_notes
        except AttributeError:
            self.cat_notes().text=formatted_notes
    def class_notes_update(self):
        # updates (or initializes then updates) customer notes
        notes=self.fetchone("""
            SELECT COALESCE(classes.notes,' ') 
            FROM classes
            JOIN categories USING (category)
            AND classes.name = %s
            AND categories.name = %s
            ;""", self.an.clas,self.an.cat)
        formatted_notes=format_notes('Class',notes[0])
        try:
            self.cust_notes_.text=formatted_notes
        except AttributeError:
            nf = self.class_notes()
            if type(nf) == Div:
                nf.text=formatted_notes
            elif type(nf) == TextInput:
                nf.value=formatted_notes
    def cust_notes_update(self):
        # updates (or initializes then updates) customer notes
        notes=self.fetchone("""
            SELECT COALESCE(customers.notes,' ') 
            FROM customers
            JOIN classes USING (class)
            JOIN categories USING (category)
            WHERE customers.name ~* %s
            AND classes.name = %s
            AND categories.name = %s
            ;""", self.an.cust,self.an.clas,self.an.cat)
        formatted_notes=format_notes('Customer',notes[0])
        try:
            self.cust_notes_.text=formatted_notes
        except AttributeError:
            nf = self.cust_notes()
            if type(nf) == Div:
                nf.text=formatted_notes
            elif type(nf) == TextInput:
                nf.value=formatted_notes