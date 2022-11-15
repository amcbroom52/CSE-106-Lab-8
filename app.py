from enum import unique
from flask import Flask, request, abort, render_template, redirect, url_for, render_template_string
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

import os
import json

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///"+os.path.join(basedir,'database.sqlite')
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
admin = Admin(app, name='microblog', template_mode='bootstrap3')
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
app.secret_key = 'super secret key'
db = SQLAlchemy(app)
db.init_app(app)


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    username = db.Column(db.String, unique=True)
    courses = db.relationship('Enrollment', backref='Student')
    authentication = db.relationship('User', backref='Student')


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    teacher = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
    time = db.Column(db.String, nullable=False)
    maxEnrolled = db.Column(db.Integer, nullable=False)
    numEnrolled = db.Column(db.Integer)
    students = db.relationship('Enrollment', backref='Course')


class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    username = db.Column(db.String, unique=True)
    courses = db.relationship('Course', backref='Teacher')
    authentication = db.relationship('User', backref='Teacher')


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    studentId = db.Column(db.Integer, db.ForeignKey('student.id'), unique=True, nullable=True)
    teacherId = db.Column(db.Integer, db.ForeignKey('teacher.id'), unique=True, nullable=True)


class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    courseId = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    studentId = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    grade = db.Column(db.Integer, nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    inUsername = request.form['username']
    inPassword = request.form['password']
    print(inUsername)
    user = User.query.filter_by(username=inUsername).first()
    print(user)
    if user is not None:
        if inPassword == user.password:
            login_user(user)
            if user.studentId is None:
                return redirect(url_for('loggedinTeacher'))
            if user.teacherId is None:
                return redirect(url_for('loggedinStudent'))
    return redirect(url_for('index'))


@app.route('/loggedinTeacher', methods=["GET"])
@login_required
def loggedinTeacher():
    if current_user.teacherId is None:
        return redirect(url_for('index'))

    current_teacher_courses = Course.query.filter_by(teacher=current_user.teacherId)
    return render_template('teacher-classes.html', courses=current_teacher_courses)


@app.route("/teacher/<course_name>", methods=['GET', 'PUT'])
@login_required
def teacher_edit(course_name):
    if current_user.teacherId is None:
        return redirect(url_for('index'))
    if request.method == "PUT":
        data = request.get_json()
        print(data)
        student = Student.query.filter_by(name=data["name"]).first()
        if student != None:
            course = Course.query.filter_by(name=course_name).first()
            enroll = Enrollment.query.filter_by(studentId=student.id, courseId=course.id).first()
            if enroll != None:
                enroll.grade = data["grade"]
                db.session.commit()
                return "success"

    if request.method == 'GET':
        listStudentIds = []
        listStudentNames = []

        grades = []

        course = Course.query.filter_by(name=course_name).first()

        listEnrolled = Enrollment.query.filter_by(courseId=course.id).order_by(Enrollment.studentId)
        # Acquire grades
        for user in listEnrolled:
            grades.append(user.grade)
        # Acquire Student Ids
        for enrolled in listEnrolled:
            listStudentIds.append(enrolled.studentId)

        enrolled_users = Student.query.filter(Student.id.in_(listStudentIds))
        # Acquire Student name
        for names in enrolled_users:
            listStudentNames.append(names.name)
        length = len(listStudentIds)

        return render_template('teacher-class-details.html', name=course_name, students=listStudentNames, grades=grades,
                               length=length)


@app.route('/loggedinStudent', methods=["GET", "POST"])
@login_required
def loggedinStudent():
    if current_user.studentId is None:
        return redirect(url_for('index'))
    if request.method == 'GET':
        all_courses = Course.query.all()
        listCourses = []
        enrolled_classes = Enrollment.query.filter_by(studentId=current_user.studentId)
        for course in enrolled_classes:
            listCourses.append(course.courseId)

        student_classes = Course.query.filter(Course.id.in_(listCourses))
        return render_template('student-view.html', courses=student_classes, all_courses=all_courses)
    if request.method == "POST":
        data = request.get_json()
        course = Course.query.filter_by(name=data["course_name"]).first()
        # already_enrolled =
        if course is not None and course.numEnrolled < course.maxEnrolled:
            enrollment = Enrollment(studentId=current_user.studentId, courseId=course.id, grade=0)
            db.session.add(enrollment)
            course.numEnrolled = course.numEnrolled + 1
            db.session.commit()
            return {"message":"course added successfully"}





@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


admin.add_view(ModelView(Student, db.session))
admin.add_view(ModelView(Course, db.session))
admin.add_view(ModelView(Teacher, db.session))
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Enrollment, db.session))

if __name__ == '__main__':
    app.run(debug=True)
