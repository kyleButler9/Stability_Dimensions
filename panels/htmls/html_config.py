from bokeh.models import Div
from os.path import join,dirname

def div_html(html,file = __file__,**kwargs):
    return Div(text=open(join(dirname(file), html)).read(),**kwargs)
