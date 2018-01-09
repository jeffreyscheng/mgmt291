from models import *
from flask import render_template
from flask import send_from_directory
from flask import request, url_for
from flask import redirect
from forms import *

# from forms import *

# FIX THIS
# test_section = Section("test_name", "Jeffrey Cheng", "password")
# test_roleplay = Roleplay("test")
# test_section.add_roleplay(test_roleplay)
check_empty = Section.query.first()
if check_empty is None:
    test_section = Section(name="test_name", instructor="Jeffrey", password_hash='')
    db.session.add(test_section)
    db.session.commit()


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico',
                               mimetype='image/vnd.microsoft.icon')


@app.route('/', methods=['GET', 'POST'])
def landing_home():
    return render_template('home.html', sections=Section.query.all())
    # return render_template('cis160.html', sections=Section.query.all())


@app.route('/about', methods=['GET', 'POST'])
def landing_about():
    return render_template('about.html')


@app.route('/add', methods=['GET', 'POST'])
def landing_add_section():
    # TODO
    form = AddRoleplayForm()
    if request.method == 'POST':
        if request.form['submit'] == 'Add Roleplay':
            current_section = Section.query.filter_by(name="test_name").first()
            current_section.add_roleplay(request.form['roleplay_name'], request.form['group_size'])
            return redirect('/')
    else:
        current_section = Section.query.filter_by(name=section_name).first()
        return render_template('add_class.html', roleplays=Roleplay.query.with_parent(current_section).all(),
                               form=form)


@app.route('/<section_name>', methods=['GET', 'POST'])
def landing_class(section_name):
    if request.method == 'POST':
        if request.form['submit'] == 'add':
            return redirect('/' + section_name + '/add')
        # else:
        #     roleplay_number = request.form['submit']
        #     return redirect('/' + section_name + '/' + roleplay_number)
    else:
        current_section = Section.query.filter_by(name="test_name").first()
        return render_template('class.html',
                               roleplays=Roleplay.query.with_parent(current_section).all(), section_name=section_name)


@app.route('/<section_name>/add', methods=['GET', 'POST'])
def landing_add_roleplay(section_name):
    form = AddRoleplayForm()
    if request.method == 'POST':
        if request.form['submit'] == 'Add Roleplay':
            current_section = Section.query.filter_by(name="test_name").first()
            current_section.add_roleplay(request.form['roleplay_name'], request.form['group_size'])
            return redirect('/' + section_name)
    else:
        current_section = Section.query.filter_by(name=section_name).first()
        return render_template('add_class.html', roleplays=Roleplay.query.with_parent(current_section).all(),
                               form=form)


@app.route('/<section_name>/<roleplay_number>', methods=['GET', 'POST'])
def landing_roleplay(section_name, roleplay_number):
    print("refreshed")
    roleplay = Roleplay.query.filter_by(section_name=section_name, number=roleplay_number).first()
    records = AttendanceRecord.query.filter_by(parent_roleplay=roleplay).all()
    print(records)
    students = [record.student_name for record in records]
    student_sign_in = SignInForm()
    template = render_template('roleplay.html', roleplay=roleplay, assignments=eval(roleplay.assignments),
                               students=students, form=student_sign_in)
    if roleplay.started:  # STARTED LOGIC)
        if request.method == 'POST':
            if request.form['submit'] == 'edit':
                return None  # TODO
            # elif request.form['submit'] == 'reset':
            #     return None  # TODO
            else:
                print("unknown POST request")
                return None
        elif request.method == 'GET':
            return template
    else:  # UNSTARTED LOGIC
        if request.method == 'POST':
            if request.form['submit'] == 'assign':
                roleplay.start()
                return redirect('/' + section_name + '/' + roleplay_number)
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


if __name__ == '__main__':
    app.run()
