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
test_section = Section(name="test_name", instructor="Jeffrey", password_hash='')
db.session.add(test_section)
db.session.commit()


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico',
                               mimetype='image/vnd.microsoft.icon')


@app.route('/', methods=['GET', 'POST'])
def landing_class():
    if request.method == 'POST':
        if request.form['submit'] == 'add':
            return redirect('/add')
        else:
            roleplay_number = request.form['submit']
            return redirect('/' + roleplay_number)
    else:
        current_section = Section.query.filter_by(name="test_name").first()
        return render_template('class.html',
                               roleplays=Roleplay.query.with_parent(current_section).all())


@app.route('/add', methods=['GET', 'POST'])
def landing_add():
    form = AddRoleplayForm()
    if request.method == 'POST':
        if request.form['submit'] == 'Add Roleplay':
            current_section = Section.query.filter_by(name="test_name").first()
            current_section.add_roleplay(request.form['roleplay_name'])
            return redirect('/')
    else:
        current_section = Section.query.filter_by(name="test_name").first()
        return render_template('add.html', roleplays=Roleplay.query.with_parent(current_section).all(),
                               form=form)


@app.route('/<roleplay_number>', methods=['GET', 'POST'])
def landing_roleplay(roleplay_number):
    roleplay = Roleplay.query.filter_by(section_name="test_name", number=roleplay_number).first()
    student_sign_in = SignInForm()
    started_template = render_template('v0_started.html', roleplay_name=roleplay.name,
                                       assignments=roleplay.assignments, form=student_sign_in)
    unstarted_template = render_template('v0_unstarted.html', roleplay_name=roleplay.name,
                                         assignments=roleplay.assignments, form=student_sign_in)
    if roleplay.started:  # STARTED LOGIC)
        if request.method == 'POST':
            if request.form['submit'] == 'edit':
                return None  # TODO
            elif request.form['submit'] == 'reset':
                return None  # TODO
            else:
                print("unknown POST request")
                return None
        elif request.method == 'GET':
            return started_template
    else:  # UNSTARTED LOGIC
        if request.method == 'POST':
            if request.form['submit'] == 'assign':
                roleplay.start()
                return started_template
            elif request.form['submit'] == 'Sign In':
                if student_sign_in.validate_on_submit():
                    roleplay.add_record(request.form['student_name'])
                    return unstarted_template
                else:
                    print("did not validate")
                    return None
            else:
                print("unknown POST request")
                return None
        elif request.method == 'GET':
            return unstarted_template


if __name__ == '__main__':
    app.run()
