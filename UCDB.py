from flask import Flask,request
from flask.json import jsonify
from flask_restful import Resource,Api
from sqlalchemy import create_engine,Column,String, Integer
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from json import loads
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey



#Database for Presential services!

#initialize app

app=Flask(__name__)
api=Api(app)

DB_FILE='DBs/CoursesDB.sqlite'

engine = create_engine('sqlite:///%s'%(DB_FILE), echo=False,connect_args={'check_same_thread': False})
Base=declarative_base()

#declare SQL Class

class Courses(Base):
    __tablename__='courses'
    id=Column(Integer, primary_key=True)
    st_id=Column(String)
    course=Column(String)
   

#initiate session
Base.metadata.create_all(engine)

Session=sessionmaker(bind=engine)
session=Session()

#declare functions for sql

def NewEntry(namei, coursei): #if the course already exists then it wont be added and returns the status code 400
    if (bool(GetEntry(namei,coursei))==True):
        return 400
    else: #otherwise create the course
        nservice=Courses(st_id=namei, course=coursei)
        session.add(nservice)
        session.commit()
        return 200

def GetCourse(namei):
    return session.query(Courses).filter(Courses.course==namei).first()

def ListCourse():
    return session.query(Courses).all()

def GetEntry(namei,coursi):
    return session.query(Courses).filter(Courses.course==coursi,Courses.st_id==namei).first()



#declare functions for REST

class CourseManage(Resource):
    def get(self): #list the courses
        raw_servicelist=ListCourse()
        finallist=[]
        for x in raw_servicelist:
            finallist.append(x.course)
            finallist.append(x.st_id)
        return jsonify(finallist)
    def post(self): #create a course
        data=loads(request.data)
        try:
            status=NewEntry(namei=data['st_id'], coursei=data['course'])
            return '',status
        except:
            return '',400

class GetCourseVer(Resource): #will check if the course exits
    def get(self,course_name):
        if bool(GetCourse(course_name))==True:
            return '',200 #course exists
        else:
            return '',404 #course doesent exist
        
class GetCoursefromST(Resource):
    def get(self,st_id,course_id):
        if bool(GetEntry(st_id,course_id))==True:
            return '',200
        else:
            return '',404

api.add_resource(CourseManage,'/')
api.add_resource(GetCourseVer,'/<course_name>/')
api.add_resource(GetCoursefromST,'/<st_id>/<course_id>/')


if __name__=='__main__':
    app.run(host='0.0.0.0',port=8004,debug=True)