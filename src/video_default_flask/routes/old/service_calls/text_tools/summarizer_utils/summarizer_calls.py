from .routes import *

def is_summary_data(**info_data):
    bool_key = info_data.get('summary') == None
    return bool_key
