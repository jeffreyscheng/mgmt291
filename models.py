import numpy as np
import pandas as pd
import itertools
from flask import Flask
from config import *
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

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

    def add_roleplay(self, name):
        associated_roleplays = Roleplay.query.with_parent(self).all()
        num_roleplays = len(associated_roleplays)
        new_roleplay = Roleplay(name=name, number=num_roleplays + 1, assignments='',
                                started=False, parent_section=self)
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

    def start(self):
        self.started = True
        db.session.commit()

    def add_record(self, student_name):
        exists = AttendanceRecord.query.with_parent(self).filter_by(student_name=student_name).first()
        if exists is None:
            a = AttendanceRecord(student_name=student_name, parent_roleplay=self)
            db.session.add(a)
            db.session.commit()

    def assign(self):
        # TODO
        encounters = pd.DataFrame(0, index=self.students, columns=self.students)
        previous_roleplays = list(self.section.roleplays)
        previous_roleplays.remove(self)
        for roleplay in previous_roleplays:
            for group in roleplay.assignments:
                members = group.values()
                all_pairs = list(itertools.combinations(members, 2))
                for pair in all_pairs:
                    stud1, stud2 = pair
                    if stud1 in self.students and stud2 in self.students:
                        encounters.loc[stud1, stud2] += 1
                        encounters.loc[stud2, stud1] += 1
        print(encounters)
        pref_lists = {}
        for student in self.students:
            student_encounters = encounters[student].to_dict()
            print(student_encounters)
            pref_lists[student] = sorted(student_encounters, key=lambda k: student_encounters[k])


class AttendanceRecord(db.Model):
    student_name = db.Column(db.String(64), primary_key=True)
    roleplay = db.Column(db.String(64), db.ForeignKey('roleplay.name'))

    def __repr__(self):
        return '<Record {}>'.format(self.student_name + ', ' + self.roleplay)
