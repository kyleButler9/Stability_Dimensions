from bokeh.models import Div
from os.path import join,dirname

def div_html(html,file = __file__,**kwargs):
    if 'args' not in kwargs:
        return Div(text=open(join(dirname(file), html)).read(),**kwargs)
    else:
        Div(text=open(join(dirname(file), html)).read().format(*kwargs['args']),**kwargs)
