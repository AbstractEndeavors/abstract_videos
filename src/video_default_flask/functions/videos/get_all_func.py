from abstract_utilities import *
text = read_from_file('all_text.py')
input(text)
texts = text.split('@call_routes_bp.route(')
def capitalizeIt(string):
    if string:
        if len(string)>1:
            string = string[0].upper()+string[1:].lower()
        else:
            string = string.upper()
    return string
def capital_underscore(string):
    new_string = ''
    for piece in string.split('_'):
        new_string+=capitalizeIt(piece)
    return new_string
def get_all_funcs():
    all_func = []
    for text in texts[1:]:
        name = text.split(',')[0]
        all_func.append(eatAll(name[1:],['/','"',"'"]))
    return all_func
input(get_all_funcs())
