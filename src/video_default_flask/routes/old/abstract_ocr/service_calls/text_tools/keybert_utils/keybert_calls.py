from .routes import *
def get_data(key,**info_data):
    return info_data.get(key)



def get_keybert_list(**info_data):
    keybert_keywords_bool = is_keybert_keywords_data(**info_data)
    keybert_combined_keywords_bool = is_keybert_combined_keywords_data(**info_data)
    keybert_bool_list = [keybert_keywords_bool,keybert_combined_keywords_bool]
    keybert_bool_key_list = ['keywords','combined_keywords']
    keybert_all_list = []
    for i,keybert_bool in enumerate(keybert_bool_list):
        if get_keybert_keywords_data(**info_data):
            keybert_key = keybert_bool_key_list[i]
            key_data = get_data(keybert_key,**info_data)
            if key_data:
                keybert_all_list += key_data
    return keybert_all_list

def is_keybert_data(**info_data):
    keybert_keywords_data = get_keybert_list(**info_data)
    return (keybert_keywords_data in [[],'',"",None])


def get_keybert_keywords_data(**info_data):
    return get_data('keywords',**info_data)

def is_keybert_keywords_data(**info_data):
    keybert_keywords = get_keybert_keywords_data(**info_data)
    bool_key = (keybert_keywords == None)
    return bool_key


def get_keybert_combined_keywords_data(**info_data):
    return get_data('combined_keywords',**info_data)

def is_keybert_combined_keywords_data(**info_data):
    keybert_combined_keywords = get_keybert_combined_keywords_data(**info_data)
    bool_key = (keybert_combined_keywords == None)
    return bool_key
