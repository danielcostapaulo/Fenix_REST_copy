from flask import Flask,request
from flask.json import jsonify
from flask_restful import Resource,Api
from sqlalchemy import create_engine,Column,String,INTEGER
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from json import loads
from requests import get
from datetime import datetime

#Database for Activity Record!

#initialize app

app=Flask(__name__)
api=Api(app)

DB_FILE='DBs/ActivityDB.sqlite'

engine = create_engine('sqlite:///%s'%(DB_FILE), echo=False)
Base=declarative_base()

#declare SQL Class

class Activities(Base):
    __tablename__='activities'
    id=Column(INTEGER,primary_key=True)
    student_id=Column(INTEGER)
    type=Column(String)
    name=Column(String)
    start_time=Column(String)
    stop_time=Column(String)
    extra=Column(String) #this column will only be useful for the academic
    def __repr__(self):
        return "<activity(student_id='%d',type='%s',name='%s',start_time='%s',stop_time='%s')>" % (self.student_id,self.type,self.name,self.start_time,self.stop_time)

#initiate session
Base.metadata.create_all(engine)

Session=sessionmaker(bind=engine)
session=Session()

#declare functions for sql

def ListActivity():
    return session.query(Activities).all()

def VerifyEntry(data): #note that True here implies that we cant add it to the DB
    list_activities=ListActivityOfStudent(data['student_id'])
    try:
        data_start=datetime.strptime(data['start_time'], '%Y-%m-%dT%H:%M:%S.000Z')
        data_start_date=data_start.date()
        data_end=datetime.strptime(data['stop_time'],'%Y-%m-%dT%H:%M:%S.000Z')
        data_end_date=data_end.date()
        if data_end<data_start:
            return True
    except:
        return True
    if data_start_date!=data_end_date:
        return True
    for activity in list_activities:
        start=datetime.strptime(activity.start_time,'%Y-%m-%dT%H:%M:%S.000Z')
        end=datetime.strptime(activity.stop_time,'%Y-%m-%dT%H:%M:%S.000Z')
        if (data_start>=start and data_start<end) or (data_end<=end and data_end>start):
            return True
    return session.query(Activities).filter(Activities.name==data['name'],Activities.student_id==data['student_id'],Activities.type==data['type'],Activities.start_time==data['start_time'],Activities.stop_time==data['stop_time'],Activities.extra==data['extra']).first()

def ListActivityOfStudent(studentid):
    return session.query(Activities).filter(Activities.student_id==studentid).all()

def NewActivity(data):
    if bool(VerifyEntry(data))==True:
        return 400
    else:
        nactivity=Activities(student_id=data['student_id'],type=data['type'],name=data['name'],start_time=data['start_time'],stop_time=data['stop_time'],extra=data['extra'])
        session.add(nactivity)
        session.commit()
        return 200

def rawtousable(raw_list): #transforms raw data into a list and removes/modifies extra
    usable_list=[]
    for x in raw_list:
        if x.type=="Academic":
            usable_list.append({"name":x.name,"student_id":x.student_id,"type":x.type,"start_time":x.start_time,"stop_time":x.stop_time,"UC":x.extra})
        else:
            usable_list.append({"name":x.name,"student_id":x.student_id,"type":x.type,"start_time":x.start_time,"stop_time":x.stop_time})

    return usable_list
#declare fucntions for REST

class CreateActivity(Resource):
    def get(self):
        raw_activitylist=ListActivity()
        activitylist=rawtousable(raw_activitylist)
        return jsonify(activitylist)
    def post(self):
        data=loads(request.data)
        try:
            if data['type']=="Personal": #personal needs no verification, it should be fine as is
                data['extra']=""
                if data['name']=="Sleep" or data['name']=="Eat" or data['name']=="Leisure" or data['name']=="Sport" or data['name']=="Other":
                    status=NewActivity(data)
                    return '',status
                else:
                    return '',400
            elif data['type']=="Administrative": #has to verify if the service exists
                ver=get('http://0.0.0.0:8001/service/{}/'.format(data['name'])).status_code
                if ver==200: #service exists,therefor it should be good to go
                    data['extra']=""
                    status=NewActivity(data)
                    return '',status
                if ver==404: #service is missing,wrong data
                    return '',400
            elif data['type']=="Academic":
                ver=get('http://0.0.0.0:8001/course/{}/{}/'.format(data['student_id'],data['extra'])).status_code
                if ver==200:
                    if data['name']=="Attend classes" or data['name']=="Study":
                        status=NewActivity(data)
                        return '',status
                    else:
                        return '',400
                if ver==404:
                    return '',400
            else:
                return '',400
        except:
            return '',400
        

class ActivityStudent(Resource):
    def get(self,student_id):
        raw_studentlist=ListActivityOfStudent(student_id)
        activitylist=rawtousable(raw_studentlist)
        return jsonify(activitylist)
    
api.add_resource(CreateActivity,'/')
api.add_resource(ActivityStudent,'/<student_id>/')

if __name__=='__main__':
    app.run(host='0.0.0.0',port=8005,debug=True)
        

