from .keybert_calls import *
from .keybert_get_data import *
from .routes import *
def get_keyword_input_keys():
     keys = ['keywords',
            'full_text',
            'info_data']
     return keys
def get_keyword_key_vars(req=None,info_data=None):
    keys = get_keyword_input_keys()
    new_data,info_data = get_key_vars(keys=keys,
                                      req=req,
                                      info_data=info_data
                                      )
    return new_data,info_data
def get_keyword_bool_key(req=None,info_data=None):
    new_data,info_data = get_keyword_key_vars(req=req,
                                              info_data=info_data)
    bool_response = is_keybert_data(**info_data)
    return get_bool_response(bool_response,info_data)
def transcribe_with_keyword_call(req=None,info_data=None):
    bool_key = get_keyword_bool_key(req=req,
                                    info_data=info_data)
    function = get_keywords_info_data
    return function,bool_key
def get_keyword_execution_variables(req=None,info_data=None):
    keys = get_keyword_input_keys()
    function,bool_key = transcribe_with_keyword_call(req=req,
                                                     info_data=info_data)
    return keys,function,bool_key

