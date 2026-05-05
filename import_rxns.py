import ast

def import_names(filename):
    file = open(filename, 'r')
    lines = file.readlines()
    file.close()
    for index in range(len(lines)):
        lines[index] = lines[index].strip()
    return lines

reaction_data = import_names('reactions.txt')
reactions = {
    'synthesis': {},
    'decomposition':{},
    'single_replacement':{},
    'double_replacement':{},
    'combustion':{}
}
for entry in reaction_data:
    if '*' in entry:
        rxn_type = entry[2:].lower()
    else:
        temp = entry.split(';')
        temp[-1] = ast.literal_eval(temp[-1])
        reactions[rxn_type][int(temp[0])] = temp[1:]

# for rxn_set in reactions:
#     print('\n',rxn_set)
#     for key,value in reactions[rxn_set].items():
#         print('\t',key,value)