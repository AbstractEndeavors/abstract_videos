
def is_summary_data(**info_data):
    bool_key = info_data.get('summary') == None
    return bool_key

from .summarizer_get_data import *
from .routes import *
def get_summary_input_keys():
     keys = ['keywords',
            'full_text',]
     return keys
def get_summary_key_vars(req=None,info_data=None):
    keys = get_summary_input_keys()
    new_data,info_data = get_key_vars(keys=keys,
                                      req=req,
                                      info_data=info_data
                                      )
    return new_data,info_data
def get_summary_bool_key(req=None,info_data=None):
    new_data,info_data = get_summary_key_vars(req=req,
                                              info_data=info_data)
    bool_response = is_summary_data(**info_data)
    return get_bool_response(bool_response,info_data)
def transcribe_with_summary_call(req=None,info_data=None):
    bool_key = get_summary_bool_key(req=req,
                                    info_data=info_data)
    function = get_summary_data
    return function,bool_key
def get_summary_execution_variables(req=None,info_data=None):
    keys = get_summary_input_keys()
    function,bool_key = transcribe_with_summary_call(req=req,
                                                     info_data=info_data)
    return keys,function,bool_key

