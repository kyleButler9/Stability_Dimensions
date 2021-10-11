from bokeh.models import Div
from os.path import join,dirname

def init_notes_div(cat,notes,file=__file__,html="notes.html"):
    if type(notes)==tuple:
            notes=notes[0]
    return div_html(html,args=(cat,notes,))
def div_html(html,file = __file__,**kwargs):
    if 'args' not in kwargs:
        return Div(text=open(join(dirname(file), html)).read(),**kwargs)
    else:
        _kwargs=dict((k,kwargs[k]) for k in kwargs if k != 'args')
        return Div(text=open(join(dirname(file), html)).read() % kwargs['args'],**_kwargs)
# def notes_to_div(cat,notes,file=__file__):
#         if type(notes)==tuple:
#             notes=notes[0]
#         return div_html("notes.html",args=(cat,notes,)).text
def format_notes(cat,notes,file=__file__,html='notes.html'):
    if type(notes)==tuple:
            notes=notes[0]
    return open(join(dirname(file), html)).read() % (cat,notes,)
