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

CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.sqlite" 
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
  maxEnrolled = db.Column(db.Integer, nullable = False)
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
  user = User.query.filter_by(username = inUsername).first()
  if user is not None:
    if inPassword == user.password:
      login_user(user)
      if current_user.studentId is None:
        return redirect(url_for('loggedinTeacher'))
      if current_user.teacherId is None:
        return redirect(url_for('loggedinStudent'))
  return redirect(url_for('index'))


@app.route('/loggedinTeacher', methods=["GET"])
@login_required
def loggedinTeacher():
    if current_user.teacherId is None:
        return redirect(url_for('index'))
    current_teacher_courses = Course.query.filter_by(teacher=current_user.teacherId)
    return render_template('teacher_page.html', courses=current_teacher_courses)


@app.route('/classPage/<int:classId>')
@login_required
def classPage(classId):
  if current_user.teacherId is None:
        return redirect(url_for('index'))
  students = Enrollment.query.filter_by(courseId = classId)
  return render_template('class.html', students = students, classId = classId)

@app.route('/changeGrade', methods=["GET", "POST"])
@login_required
def changeGrade():
  if current_user.teacherId is None:
        return redirect(url_for('index'))
  studentID = request.form['studentId']
  course = request.form['course']
  studentGrade = request.form['studentGrade']
  enroll = Enrollment.query.filter_by(studentId = studentID, courseId = course).first()
  enroll.grade = studentGrade
  db.session.commit()
  return redirect(url_for('classPage', classId=course))

@app.route('/decreaseGrade/<studentId>/<courseId>')
@login_required
def decreaseGrade(studentId, courseId):
  if current_user.teacherId is None:
    return redirect(url_for('index'))
  enroll = Enrollment.query.filter_by(studentId = studentId, courseId = courseId).first()
  enroll.grade -= 1
  print(studentId)
  print(courseId)
  print(enroll)
  db.session.commit()
  return redirect(url_for('classPage', classId=courseId))

@app.route('/increaseGrade/<studentId>/<courseId>')
@login_required
def increaseGrade(studentId, courseId):
  if current_user.teacherId is None:
    return redirect(url_for('index'))
  enroll = Enrollment.query.filter_by(studentId = studentId, courseId = courseId).first()
  enroll.grade += 1
  print(studentId)
  print(courseId)
  print(enroll)
  db.session.commit()
  return redirect(url_for('classPage', classId=courseId))

@app.route('/back')
@login_required
def back():
  if current_user.teacherId is None:
    return redirect(url_for('index'))
  return redirect(url_for('loggedinTeacher'))

@app.route('/loggedinStudent')
@login_required
def loggedinStudent():
  if current_user.studentId is None:
    return redirect(url_for('index'))
  classes = Course.query.all()
  currentStudent = Student.query.filter_by(id = current_user.Student.id).first()
  enrollments = Enrollment.query.filter_by(studentId = currentStudent.id)
  courses = []
  for item in enrollments:
    courses.append(item.Course)
  return render_template('student_page.html', classes=classes, courses=courses)

@app.route('/addClass/<int:classId>', methods=['GET', 'POST'])
@login_required
def addClass(classId):
  print(classId)
  course = Course.query.filter_by(id = classId).first()
  print(course)
  if Enrollment.query.filter_by(studentId = current_user.Student.id, courseId = course.id).first() is not None or course.numEnrolled == course.maxEnrolled:
    return redirect(url_for('loggedinStudent'))
  enroll = Enrollment(courseId = course.id, studentId = current_user.Student.id, grade = 100)
  course.numEnrolled += 1
  db.session.add(enroll)
  db.session.commit()
  return redirect(url_for('loggedinStudent'))

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


