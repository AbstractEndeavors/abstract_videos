from abstract_utilities import safe_dump_to_file,get_bool_response
from .functions import *
def handle_bool_response(bool_response,function,new_data,info_data):
    logger.info(f"bool_key == {bool_response}")
    if bool_response:
        info = function(**new_data)
        info_data = update_json_data(info_data,info,keys=True)
    safe_dump_to_file(data=info_data,file_path=get_video_info_path(**info_data))
    return info_data
def execute_if_bool(bool_key,function,keys,req=None,info_data=None):
    new_data,info_data = get_key_vars(keys,req,info_data)
    bool_response = get_bool_response(bool_key,info_data)
    info_data = handle_bool_response(bool_response,
                                     function,
                                     new_data,
                                     info_data
                                     )
    return info_data
