from flask import Flask, render_template, request, session, flash # type: ignore
import random, re
from markupsafe import Markup # type: ignore
from copy import deepcopy

from flask.sessions import NullSession # type: ignore
from import_rxns import reactions, all_reactions

app = Flask(__name__)
app.config['DEBUG'] = True
app.secret_key = 'H&7v$K2#mP!9Lz@5qR*4jX^8sB(1nW%6'

def check_type_answers(prompts, ans):
    num_correct = 0
    for index in range(len(prompts)):
        if is_overlapping_type(prompts[index], ans[index]):
            num_correct += 1
            if ans[index] == 'synthesis':
                flash('Correct!  :-) (Also a combustion reaction.)', 'correct')
            else:
                flash('Correct!  :-) (Also a synthesis reaction.)', 'correct')
        elif ans[index] == prompts[index][-1]:
            num_correct += 1
            flash('Correct!  :-)', 'correct')
        else:
            flash('Nope!', 'error')

    return num_correct

def is_overlapping_type(reaction, answ):
    if reaction[-1] != 'synthesis' and reaction[-1] != 'combustion':
        return False
    # Split reaction into reactants and products sections.
    rxn_split = reaction[0].split('->')
    # Split products into separate compounds.
    prod_split = rxn_split[1].split(',')
    # Synthesis reactions have only one product. Combustion reactions have O2 as a reactant.
    if ',O2' in rxn_split[0] and len(prod_split) == 1 and (answ == 'synthesis' or answ == 'combustion'):
        return True
    # The equations in reactions.txt have been chosen to avoid other overlaps.
    # Redox reactions and acid/base reactions are not assessed by this app.
    return False

def check_bce_answers(coeffs, ans):
    bce_correct = 0
    for index in range(len(coeffs)):
        if coeffs[index] == ans[index]:
            bce_correct += 1
            flash('Correct!  :-)', 'correct')
        elif not proper_coeffs(ans[index]):
            flash('Coefficients must be positive, whole numbers.', 'error')
        elif are_multiples(coeffs[index], ans[index]):
            bce_correct += 0.5
            flash(f'The equation is balanced, but reduce your coefficients to {coeffs[index]}.', 'error')
        else:
            wrong_coeffs = id_mistakes(coeffs[index], ans[index])
            num_incorrect = wrong_coeffs.count('X')
            if num_incorrect == 1:
                flash(f'You have {num_incorrect} incorrect coefficient. {wrong_coeffs}', 'error')
            else:
                flash(f'You have {num_incorrect} incorrect coefficients. {wrong_coeffs}', 'error')
    return bce_correct

def proper_coeffs(values):
    for value in values:
        if value < 1:
            return False
    return True

def are_multiples(coefs, ans):
    if ans[0] != coefs[0] and ans[0] < coefs[0]:
        return False
    multiplier = ans[0]/coefs[0]
    for index in range(1, len(coefs)):
        if multiplier != ans[index]/coefs[index]:
            return False
    return True

def id_mistakes(corrects, ans):
    mistakes = []
    for index in range(len(corrects)):
        if corrects[index] == ans[index]:
            mistakes.append(str(ans[index]))
        else:
            mistakes.append('X')
    return ', '.join(mistakes)

@app.template_filter('subscript')
def render_equation(raw_rxn):
    # Add whitespace, blanks and '+' symbols to the unbalanced reaction.
    raw_rxn = raw_rxn.replace(',', ' + __').replace('->', ' -> __')

    # Add blank in front of first chemical formula.
    raw_rxn = '__' + raw_rxn

    # Use regex to find digits and wrap them in <sub> tags.
    final_rxn = re.sub(r'(\d+)', r'<sub>\1</sub>', raw_rxn)
    return final_rxn

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
        session.clear()
        session['num_attempted'] = 0
        session['numCorrect'] = 0
    return render_template('index.html', title = 'Balancing Practice')

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

@app.route('/balancing_practice', methods=['POST', 'GET'])
def balancing_practice():
    page_title = 'Balancing Practice, Level 1'
    template_name = 'balancing_practice'
    answers = []
    if request.method == 'POST':
        questions = session['questions']
        for index in range(len(questions)):
            row_answers = []
            num_inputs = questions[index][1].count('+') + 2
            for entry in range(num_inputs):
                answer = request.form['box'+str(index+1)+'_'+str(entry+1)]
                if answer == '':
                    answer = '1'
                elif not answer.isdigit() and '-' not in answer:
                    answer = '1'
                row_answers.append(int(answer))
            answers.append(tuple(row_answers))
        num_correct = check_bce_answers(session['check_these'], answers)
        if session['first_try']:
            session['first_try'] = False
            session['numCorrect'] += num_correct
            session['first_score'] = session['numCorrect']
    else:
        session['first_try'] = True
        questions = []
        coefficients = []
        picked = []
        while len(questions) < 3:
            rxn = random.choice(all_reactions)
            if rxn[0] not in picked:
                picked.append(rxn[0])
                coefficients.append(rxn[1])
                questions.append([len(questions)+1, Markup(render_equation(rxn[0]))])
        session['questions'] = deepcopy(questions)
        session['check_these'] = deepcopy(coefficients)
        session['num_attempted'] += len(questions)
    
    percentage = round(session['numCorrect']/session['num_attempted']*100,1)
    return render_template('balancing_practice.html',title='Balancing Practice', page_title = page_title, 
            template = template_name, questions = questions, answers = answers, percentage = percentage)

@app.route('/balancing_practice_2', methods=['POST', 'GET'])
def balancing_practice_2():
    page_title = 'Balancing Practice, Level 2'
    template_name = 'balancing_practice_2'
    answers = []
    if request.method == 'POST':
        pass
    else:
        session['first_try'] = True
        questions = []
    
    return render_template('balancing_practice_2.html',title='Balancing Practice', page_title = page_title, 
            template = template_name, questions = questions, answers = answers)

@app.route('/types_practice', methods=['POST', 'GET'])
def types_practice():
    page_title = 'Identify Reaction Types'
    template_name = 'types_practice'
    rxn_types = list(reactions.keys())
    answers = []
    if request.method == 'POST':
        questions = session['questions']
        for index in range(len(questions)):
            answers.append(request.form['answer_'+str(index+1)])  #Pull user answers into a list.
        num_correct = check_type_answers(session['check_these'], answers)
        if session['first_try']:
            session['first_try'] = False
            session['numCorrect'] += num_correct
            session['first_score'] = session['numCorrect']
    else:
        session['first_try'] = True
        questions = []
        choices = []
        picked = []
        while len(questions) < 5:
            type_choice = random.choice(rxn_types)
            rxn_number = random.choice(range(1,len(reactions[type_choice])))
            rxn = reactions[type_choice][rxn_number]
            if rxn[0] not in picked:
                picked.append(rxn[0])
                choices.append([rxn[0], type_choice])
                questions.append([len(questions)+1, Markup(render_equation(rxn[0]))])
        session['questions'] = deepcopy(questions)
        session['check_these'] = deepcopy(choices)
        session['num_attempted'] += len(questions)

    percentage = round(session['numCorrect']/session['num_attempted']*100,1)
    return render_template('types_practice.html',title='Identify Reaction Types', page_title = page_title, template = template_name,
        rxn_types = rxn_types, questions = questions, percentage = percentage, answers = answers)

if __name__ == '__main__':
    app.run()