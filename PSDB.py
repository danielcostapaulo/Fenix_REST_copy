from flask import Flask,request
from flask.json import jsonify
from flask_restful import Resource,Api
from sqlalchemy import create_engine,Column,String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from json import loads

from rospy import Service

#Database for Presential services!

#initialize app

app=Flask(__name__)
api=Api(app)

DB_FILE='DBs/ServicesDB.sqlite'

engine = create_engine('sqlite:///%s'%(DB_FILE), echo=False)
Base=declarative_base()

#declare SQL Class

class Services(Base):
    __tablename__='service'
    name=Column(String,primary_key=True)

#initiate session
Base.metadata.create_all(engine)

Session=sessionmaker(bind=engine)
session=Session()

#declare functions for sql

def NewEntry(namei): #if the service already exists then it wont be added and returns the status code 400
    if bool(GetService(namei))==True:
        return 400
    else: #otherwise create the services
        nservice=Services(name=namei)
        session.add(nservice)
        session.commit()
        return 200

def GetService(namei):
    return session.query(Services).filter(Services.name==namei).first()

def ListService():
    return session.query(Services).all()

def DeleteService(namei):
    if bool(GetService(namei))!=True:
        return 400
    else:
        to_del=GetService(namei)
        session.delete(to_del)
        session.commit()
        return 200

#declare functions for REST

class ServiceManage(Resource):
    def get(self): #list the services
        raw_servicelist=ListService()
        finallist=[]
        for x in raw_servicelist:
            finallist.append(x.name)
        return jsonify(finallist)
    def post(self): #create a service
        data=loads(request.data)
        try:
            status=NewEntry(namei=data['name'])
            return '',status
        except:
            return '',400
            
class GetServiceVer(Resource): #will check if the service exits
    def get(self,service_name):
        if bool(GetService(service_name))==True:
            return '',200 #service exists
        else:
            return '',404 #service doesent exist
    def delete(self,service_name):
        try:
            status=DeleteService(service_name)
            return '',status
        except:
            return '',400
        

api.add_resource(ServiceManage,'/')
api.add_resource(GetServiceVer,'/<service_name>/')


if __name__=='__main__':
    app.run(host='0.0.0.0',port=8002,debug=True)