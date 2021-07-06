from bokeh.models import Div
from os.path import join,dirname

def div_html(html,file = __file__,**kwargs):
    if 'args' not in kwargs:
        return Div(text=open(join(dirname(file), html)).read(),**kwargs)
    else:
        _kwargs=dict((k,adict[k]) for k in kwargs if k != 'args')
        return Div(text=open(join(dirname(file), html)).read() % kwargs['args'],**_kwargs)
