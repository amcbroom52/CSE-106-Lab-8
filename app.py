from enum import unique
from flask import Flask
from flask import request
from flask import abort, render_template
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

import os
import json

app = Flask(__name__)

CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.sqlite" 
db = SQLAlchemy(app) 
db.init_app(app)


class Student(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String, nullable=False)
  username = db.Column(db.String, unique=True, nullable=False)
  def __init__(self, name, username):
    self.name = name
    self.username = username

class Course(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String, unique=True, nullable=False)
  teacher = db.Column(db.Integer, nullable=False)
  time = db.Column(db.String, nullable=False)
  maxEnrolled = db.Column(db.Integer, nullable = False)
  numEnrolled = db.Column(db.Integer)

class Teacher(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String, nullable=False)
  username = db.Column(db.String, unique=True, nullable=False)

class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String, unique=True, nullable=False)
  password = db.Column(db.String, nullable=False)

class Enrollment(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  courseId = db.Column(db.Integer, nullable=False)
  studentId = db.Column(db.Integer, nullable=False)
  grade = db.Column(db.Integer, nullable=False)




@app.route('/')
def index():
    return render_template('index.html')



if __name__ == '__main__':
  app.run()

