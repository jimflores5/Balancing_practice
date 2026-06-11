import ast

def import_names(filename):
    file = open(filename, 'r')
    lines = file.readlines()
    file.close()
    for index in range(len(lines)):
        lines[index] = lines[index].strip()
    return lines

reaction_data = import_names('reactions.txt')
types_data = import_names('types_tutorial.txt')
# Create an empty dictionary to hold the reactions to balance.
# Each reaction falls into 1 of 5 types.
# For now, we will ignore overlaps between combustion and synthesis.
reactions = {
    'synthesis': {},
    'decomposition':{},
    'single_replacement':{},
    'double_replacement':{},
    'combustion':{}
}

types_of_rxns_text = {
    'synthesis': [],
    'decomposition':[],
    'single_replacement':[],
    'double_replacement':[],
    'combustion':[]
}

# Create an empty list to hold all the reactions with no reaction type info.
all_reactions = []

for entry in reaction_data:
    # Check if entry is a header for a reaction type.
    if '*' in entry:
        rxn_type = entry[2:].lower()
    else:
        # Split the entry into 3 pieces - index, reaction, answer.
        temp = entry.split(';')
        # Convert the string answer into a tuple.
        temp[-1] = ast.literal_eval(temp[-1])
        # Add the reaction to the appropriate dictionary.
        reactions[rxn_type][int(temp[0])] = temp[1:]
        all_reactions.append(temp[1:])

for entry in types_data:
    if '*' in entry:
        rxn_type = entry[2:].lower()
    else:
        types_of_rxns_text[rxn_type].append(entry)