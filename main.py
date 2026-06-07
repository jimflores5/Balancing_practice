from flask import Flask, render_template, request, session, redirect
import random
import re

from flask.sessions import NullSession
from import_rxns import reactions

app = Flask(__name__)
app.config['DEBUG'] = True
app.secret_key = 'H&7v$K2#mP!9Lz@5qR*4jX^8sB(1nW%6'

@app.template_filter('subscript')
def subscript(value):
    # This regex finds digits and wraps them in <sub> tags
    return re.sub(r'(\d+)', r'<sub>\1</sub>', value)

@app.route('/submit', methods=['POST'])
def submit():
    questions = session.get('questions')
    results = {}
    for id, data in questions.items():
        # Get coefficients for this reaction (e.g., c1_r1, c1_r2, c1_p1)
        keys = [k for k in request.form if k.startswith(f'c{id}_')]

        # Sort keys: Reactants (r) first, then Products (p), then by index
        def chem_sort(key):
            # key format: 'c1_r2' -> side_part is 'r2'
            side_part = key.split('_')[1] 
            side = side_part[0]  # 'r' or 'p'
            index = int(side_part[1:])
            # Assign priority 0 to 'r' and 1 to 'p' to ensure correct left-to-right order
            priority = 0 if side == 'r' else 1
            return (priority, index)

        sorted_keys = sorted(keys, key=chem_sort)
        
        user_values = tuple(int(request.form[k]) for k in sorted_keys)
        correct_values = data[1]
        print(user_values, correct_values)
    return "Rutabagas!"

@app.route('/rxns', methods = ['GET', 'POST'])
def rxns():
    if request.method == 'POST':
        rxn_type = request.form['rxn_type']
        keys = random.sample(range(1, len(reactions[rxn_type])+1), 3)
        chosen_rxns = {}
        for index in range(len(keys)):
            chosen_rxns[index+1] = reactions[rxn_type][index+1]
        session['questions'] = chosen_rxns

        return render_template('rxns.html', title = 'Balancing Practice', reactions = chosen_rxns)

@app.route('/', methods = ['GET', 'POST'])
def index():
    if request.method == 'POST':
        pass
    else:
        rxn_types = list(reactions.keys())
    return render_template('index.html', reactions = rxn_types, title = 'Balancing Practice')

if __name__ == '__main__':
    app.run()