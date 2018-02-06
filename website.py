from models import *
from flask import render_template
from flask import send_from_directory
from flask import request, url_for
from flask import redirect
from flask_basicauth import BasicAuth
from forms import *

app.config['BASIC_AUTH_USERNAME'] = 'instructor'
app.config['BASIC_AUTH_PASSWORD'] = 'negotiationsarefun'

basic_auth = BasicAuth(app)


def reverse_name(last_first):
    names = last_first.split(', ')
    return names[1] + ' ' + names[0]


# file-input.py
even_roster = []
odd_roster = []
with open('odd_roster.txt', 'r') as file:
    for line in file:
        odd_roster.append(reverse_name(line.strip()))
with open('even_roster.txt', 'r') as file:
    for line in file:
        even_roster.append(reverse_name(line.strip()))
even_roster.sort()
odd_roster.sort()
roster = even_roster + odd_roster
roster.sort()


# check_empty = Section.query.first()
# if check_empty is None:
#     test_section = Section(name="test_name", instructor="Jeffrey", password_hash='')
#     db.session.add(test_section)
#     db.session.commit()

# negotiationsarefun

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico',
                               mimetype='image/vnd.microsoft.icon')


# TODO :  password-lock on add
@app.route('/', methods=['GET', 'POST'])
def landing_home():
    if request.method == 'POST':
        if request.form['submit'] == 'add':
            return redirect('/add')
    return render_template('home.html', sections=Section.query.all(), odds=odd_roster, evens=even_roster)
    # return render_template('cis160.html', sections=Section.query.all())


# @app.route('/<path:destination>/login', methods=['GET', 'POST'])
# def landing_login(destination):
#     form = LoginForm()
#     if request.method == 'POST':
#         print(request.form)
#         if request.form['submit'] == 'Instructor Sign In':
#             try:
#                 curr_section = Section.query.filter_by(name=request.form['class_name']).first()
#                 actual_hash = curr_section.password_hash
#                 if hash_string(request.form['password']) == actual_hash:
#                     return redirect('/' + destination)
#                 else:
#                     return render_template('login.html', form=form, failed=True)
#             except AttributeError
#                 return render_template('login.html', form=form, failed=True)
#     return render_template('login.html', form=form, failed=False)
#     # return render_template('cis160.html', sections=Section.query.all())


@app.route('/about', methods=['GET', 'POST'])
def landing_about():
    return render_template('about.html')


@app.route('/add', methods=['GET', 'POST'])
@basic_auth.required
def landing_add_section():
    form = AddSectionForm()
    if request.method == 'POST':
        if request.form['submit'] == 'Add Section':
            print(request.form)
            name = request.form['section_name']
            # new_section = Section(name=name, instructor=request.form["instructor_name"],
            #                       password_hash=hash_string(request.form["password"]))
            new_section = Section(name=name, instructor=request.form["instructor_name"])
            db.session.add(new_section)
            db.session.commit()
            return redirect('/' + name)
    else:
        return render_template('add_class.html', form=form)


@app.route('/<section_name>', methods=['GET', 'POST'])
def landing_class(section_name):
    if request.method == 'POST':
        if request.form['submit'] == 'add':
            return redirect('/' + section_name + '/add')
        # else:
        #     roleplay_number = request.form['submit']
        #     return redirect('/' + section_name + '/' + roleplay_number)
    else:
        current_section = Section.query.filter_by(name=section_name).first()
        return render_template('class.html',
                               roleplays=Roleplay.query.with_parent(current_section).all(), section_name=section_name)


@app.route('/<section_name>/add', methods=['GET', 'POST'])
@basic_auth.required
def landing_add_roleplay(section_name):
    form = AddRoleplayForm()
    if request.method == 'POST':
        if request.form['submit'] == 'Add Roleplay':
            current_section = Section.query.filter_by(name=section_name).first()
            current_section.add_roleplay(request.form['roleplay_name'], request.form['group_size'])
            return redirect('/' + section_name)
    else:
        current_section = Section.query.filter_by(name=section_name).first()
        return render_template('add_roleplay.html', roleplays=Roleplay.query.with_parent(current_section).all(),
                               form=form)


@app.route('/<section_name>/<roleplay_number>', methods=['GET', 'POST'])
def landing_roleplay(section_name, roleplay_number):
    print("refreshed")
    roleplay = Roleplay.query.filter_by(section_name=section_name, number=roleplay_number).first()
    records = AttendanceRecord.query.with_parent(roleplay).all()
    print(records)
    students = [record.student_name for record in records]
    student_sign_in = SignInForm()
    print(roleplay.parent_section)
    print(roster)
    print(eval(roleplay.assignments))
    # roleplay.assignments = '[]'
    # roleplay.started = True
    # db.session.add(roleplay)
    # db.session.commit()
    template = render_template('roleplay.html', roleplay=roleplay, assignments=eval(roleplay.assignments),
                               students=students, form=student_sign_in, roster=roster)
    if roleplay.started:  # STARTED LOGIC
        print("GOT HERE")
        print(roleplay.assignments)
        if roleplay.assignments == '' or roleplay.assignments == '[]' or roleplay.assignments == '{}':
            roleplay.start()
        if request.method == 'POST':
            if request.form['submit'] == 'edit':
                return redirect('/' + section_name + '/' + roleplay_number + '/edit')
            elif request.form['submit'] == 'reset':
                return redirect('/' + section_name + '/' + roleplay_number + '/reset')
            else:
                print("unknown POST request")
                return None
        elif request.method == 'GET':
            roleplay = Roleplay.query.filter_by(section_name=section_name, number=roleplay_number).first()
            return render_template('roleplay.html', roleplay=roleplay, assignments=eval(roleplay.assignments),
                                   students=students, form=student_sign_in)
    else:  # UNSTARTED LOGIC
        if request.method == 'POST':
            if request.form['submit'] == 'assign':
                return redirect('/' + section_name + '/' + roleplay_number + '/login')
            elif request.form['submit'] == 'Sign In':
                if student_sign_in.validate_on_submit():
                    roleplay.add_record(request.form['student_name'])
                    return redirect('/' + section_name + '/' + roleplay_number)
                else:
                    print("did not validate")
                    return None
            else:
                print("unknown POST request")
                return None
        elif request.method == 'GET':
            return template


@app.route('/<section_name>/<roleplay_number>/reset', methods=['GET', 'POST'])
@basic_auth.required
def landing_reset(section_name, roleplay_number):
    roleplay = Roleplay.query.filter_by(section_name=section_name, number=roleplay_number).first()
    roleplay.started = False
    roleplay.assignments = []
    db.session.add(roleplay)
    db.session.commit()
    return redirect('/' + section_name + '/' + roleplay_number)


@app.route('/<section_name>/<roleplay_number>/login', methods=['GET', 'POST'])
@basic_auth.required
def landing_start(section_name, roleplay_number):
    roleplay = Roleplay.query.filter_by(section_name=section_name, number=roleplay_number).first()
    roleplay.started = True
    db.session.commit()
    return redirect('/' + section_name + '/' + roleplay_number)

# [('Gary', 'Meghna Sreenivas', 'Edward Haddad'), ('Vasudha Rajgarhia', "George Pandya']", 'Steven Delcarson'), ('Maxim Zats', "Mihir Shah']", "Chloe Wilson']"), ("Steven Delcarson']", 'Chloe Wilson', 'Shehryar Khursheed'), ('Giancarlo Marconi', "Meghna Sreenivas']", "Maxim Zats']"), ('Lisaho Abe', "Sabrina Hagan']", "['Wai Wu"), ("['Jessica Le", 'Ricardo Pena', "['Gary"), ("['Anshul Tripathi", "['Sophia Cen", "['Alison Weiss"), ("['Cheryl Feig", 'Jessica Le', 'Cheryl Feig'), ('Anshul Tripathi', 'Hari Kumar', 'Sabrina Hagan'), ('Peter Ojo', "Sruti Suresh']", "Maxwell Abram']"), ('Nadira Berman', 'Mihir Shah', "['Erin-Marie Deytiquez"), ('Erin-Marie Deytiquez', 'Deanna Taylor', 'Jackson Unikel'), ('Sebastian', "Gahyun Jung']", 'Shichen Zhang'), ("Shichen Zhang']", "['Nadira Berman", 'George Pandya'), ('Sruti Suresh', 'Tiffany Yung', "Edward Haddad']"), ("Krzysztof Jakubowski']", 'Sydney Shiffman', 'Collin Loughead'), ('Krzysztof Jakubowski', 'Freddie', 'Maxwell Abram'), ('Kasra Koushan', "Tiffany Yung']", 'Steve Zheng'), ('Samuel Roth', "['Lisaho Abe", 'Olutoni Oloko'), ('Alison Weiss', 'Victoria Sacchetti', 'Yajaira Torres'), ("['Steve Zheng", 'Wai Wu', 'Jacob Snyder'), ("['Catherine", 'George Pennacchi', 'Gahyun Jung', 'Sophia Cen'), ("['George Pennacchi", "['Kasra Koushan", "['Vasudha Rajgarhia", 'Catherine')]


@app.route('/<section_name>/<roleplay_number>/edit', methods=['GET', 'POST'])
@basic_auth.required
def landing_edit_roleplay(section_name, roleplay_number):
    form = EditRoleplayForm()
    current_roleplay = Roleplay.query.filter_by(section_name=section_name, number=roleplay_number).first()
    if request.method == 'POST':
        if request.form['submit'] == 'Edit Assignments':
            edit_string = request.form['assignments']
            current_roleplay.edit_assignments(edit_string)
            return redirect('/' + section_name + '/' + roleplay_number)
    else:
        print("CURR ASSIGNMENT")
        print(current_roleplay.assignments)
        assignments_string = current_roleplay.assignments.replace('(', '').replace('), ', '\n').replace('),', '\n')
        assignments_string = assignments_string[1:len(assignments_string) - 2]
        count = assignments_string.count("\n")
        form.assignments.default = assignments_string
        form.process()
        return render_template('edit_roleplay.html', roleplays=current_roleplay, assignments_string=assignments_string,
                               form=form, count=count)


if __name__ == '__main__':
    app.run()
