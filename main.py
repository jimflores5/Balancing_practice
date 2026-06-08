from flask import Flask, render_template, request, session, redirect # type: ignore
import random
import re

from flask.sessions import NullSession # type: ignore
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

@app.route('/rxn_types/<page>', methods=['POST', 'GET'])
def rxn_types(page):
    page_title = 'Types of Reactions'
    num_pages = 7
    template_name = 'rxn_types'
    page = int(page)
    if request.method == 'POST':
        pass

    return render_template('rxn_types.html',title='Types of Reactions', page = page, page_title = page_title, 
            num_pages = num_pages, template = template_name)

@app.route('/balancing_rxns/<page>', methods=['POST', 'GET'])
def balancing_rxns(page):
    page_title = 'Balancing Chemical Equations'
    num_pages = 3
    template_name = 'balancing_rxns'
    page = int(page)
    if request.method == 'POST':
        pass

    if page == 1:
        subheading = 'Conservation of Mass'
    elif page == 2:
        subheading = 'Steps to balance a reaction.'
    else:
        subheading = 'First Practice!'
    return render_template('balancing_rxns.html',title='How to Balance a Reaction', page = page, page_title = page_title, 
            num_pages = num_pages, template = template_name, subheading = subheading)

@app.route('/predict_prods/<page>', methods=['POST', 'GET'])
def predict_prods(page):
    page_title = 'Predicting Products'
    num_pages = 3
    template_name = 'predict_prods'
    page = int(page)
    if request.method == 'POST':
        pass

    if page == 1:
        subheading = 'Sometimes, not all of the chemical formulas will be given.'
    elif page == 2:
        subheading = 'Predicting products for Synthesis, Single Replacement, and Double Replacement reactions.'
    else:
        subheading = 'Predicting products for combustion reactions.'
    return render_template('predict_prods.html',title='Predicting Products', page = page, page_title = page_title, 
            num_pages = num_pages, template = template_name, subheading = subheading)

@app.route('/balancing_practice/<page>', methods=['POST', 'GET'])
def balancing_practice(page):
    page_title = 'Balancing Practice'
    num_pages = 2
    template_name = 'balancing_practice'
    page = int(page)
    if request.method == 'POST':
        pass
    else:
        session['first_try'] = True
        session['num_attempted'] = 0
        session['numCorrect'] = 0
        if page == 1:
            subheading = 'Balancing Equations, Level 1'
        else:
            subheading = 'Balancing Equations, Level 2'
    return render_template('balancing_practice.html',title='Balancing Practice', page = page, page_title = page_title, 
            num_pages = num_pages, template = template_name, subheading = subheading)

@app.route('/types_practice', methods=['POST', 'GET'])
def types_practice():
    page_title = 'Identify Reaction Types'
    template_name = 'types_practice'
    if request.method == 'POST':
        pass
    else:
        session['first_try'] = True
        session['num_attempted'] = 0
        session['numCorrect'] = 0
        rxn_types = list(reactions.keys())
        questions = {}
        while len(questions) < 3:
            type_choice = random.choice(rxn_types)
            rxn_number = random.choice(range(1,len(reactions[type_choice])))
            rxn = reactions[type_choice][rxn_number]
            if rxn[0] not in questions:
                questions[rxn[0]] = [len(questions)+1, type_choice]

    return render_template('types_practice.html',title='Identify Reaction Types', page_title = page_title, template = template_name,
        rxn_types = rxn_types, questions = questions)

if __name__ == '__main__':
    app.run()