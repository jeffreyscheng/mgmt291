import numpy as np
import pandas as pd
import itertools
from flask import Flask
from config import *
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from stableroomate import stableroomate

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
db.session.expire_on_commit = False
migrate = Migrate(app, db)


class Section(db.Model):
    name = db.Column(db.String(64), primary_key=True)
    instructor = db.Column(db.String(64), index=True)
    password_hash = db.Column(db.String(128))
    roleplays = db.relationship('Roleplay', backref='parent_section', lazy='dynamic')

    # def __init__(self, name, instructor, password):
    #     self.name = name
    #     # self.students = students # unnecessary
    #     self.instructor = instructor
    #     self.password = password
    #     self.roleplays = []
    #     # self.students = {}  # e.g. students['Jeffrey Cheng'] = ['partner 1', 'partner 2']

    def add_roleplay(self, name, group_size):
        associated_roleplays = Roleplay.query.with_parent(self).all()
        num_roleplays = len(associated_roleplays)
        new_roleplay = Roleplay(name=name, number=num_roleplays + 1, assignments='[]',
                                started=False, parent_section=self, group_size=group_size)
        db.session.add(new_roleplay)
        db.session.commit()
        print("TESTING IN ADD_ROLEPLAY")
        print(Roleplay.query.all())

    def __repr__(self):
        return '<Section {}>'.format(self.name)


class Roleplay(db.Model):
    name = db.Column(db.String(64), primary_key=True)
    number = db.Column(db.Integer, index=True)
    assignments = db.Column(db.String(4000))
    started = db.Column(db.Boolean)
    section_name = db.Column(db.String(64), db.ForeignKey('section.name'))
    group_size = db.Column(db.Integer)
    attendees = db.relationship('AttendanceRecord', backref='parent_roleplay', lazy='dynamic')

    def __repr__(self):
        return '<Roleplay {}>'.format(self.name + ': ' + str(self.number))

    # def __init__(self, name):
    #     self.name = name
    #     self.number = -1
    #     self.students = []
    #     self.assignments = []
    #     self.started = False
    #     self.section = None

    def add_record(self, student_name):
        exists = AttendanceRecord.query.with_parent(self).filter_by(student_name=student_name).first()
        if exists is None:
            a = AttendanceRecord(id=self.name + ":" + student_name,
                                 student_name=student_name, parent_roleplay=self)
            db.session.add(a)
            db.session.commit()

    def start(self):
        self.started = True
        # gets preferences
        records = AttendanceRecord.query.with_parent(self).all()
        students = [record.student_name for record in records]
        encoding = {rank: students[rank - 1] for rank in range(1, len(students) + 1)}
        reverse_encoding = {encoding[key]: key for key in encoding}
        encounters = pd.DataFrame(0, index=students, columns=students)
        previous_roleplays = Roleplay.query.with_parent(self.parent_section).all()
        previous_roleplays.remove(self)
        print(previous_roleplays)
        for roleplay in previous_roleplays:
            for group in eval(roleplay.assignments):
                all_pairs = list(itertools.combinations(group, 2))
                for pair in all_pairs:
                    stud1, stud2 = pair
                    if stud1 in students and stud2 in students:
                        encounters.loc[stud1, stud2] += 1
                        encounters.loc[stud2, stud1] += 1
        print(encounters)
        pref_lists = {}
        for student in students:
            student_encounters = encounters[student].to_dict()
            pref_list = sorted(student_encounters, key=lambda k: student_encounters[k])
            pref_list.remove(student)
            pref_lists[reverse_encoding[student]] = [reverse_encoding[student] for student in pref_list]
        print(pref_lists)
        # TODO: assign
        if self.group_size == 2:
            matching = stableroomate(pref_lists)
            print(matching)
            assignments = []
            for i in range(1, len(students) + 1):
                if i in matching:
                    pair = encoding[i], encoding[matching[i]]
                    assignments.append(pair)
                    del matching[matching[i]]
                    del matching[i]
            print(assignments)
            self.assignments = str(assignments)
        db.session.commit()
        print("FINISHED ASSIGNING")


class AttendanceRecord(db.Model):
    id = db.Column(db.String(64), primary_key=True)
    student_name = db.Column(db.String(64))
    roleplay = db.Column(db.String(64), db.ForeignKey('roleplay.name'))

    def __repr__(self):
        return '<Record {}>'.format(self.student_name + ', ' + self.roleplay)
