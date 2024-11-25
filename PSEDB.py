from sqlite3 import IntegrityError
from tkinter.tix import INTEGER
from flask import Flask,request
from flask.json import jsonify
from flask_restful import Resource,Api
from sqlalchemy import create_engine,Column,String, Integer
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from json import loads
from requests import get

#Database for Presential services evaluation!

#initialize app

app=Flask(__name__)
api=Api(app)

DB_FILE='DBs/PSEDB.sqlite'

engine = create_engine('sqlite:///%s'%(DB_FILE), echo=False,connect_args={'check_same_thread': False})
Base=declarative_base()

#declare SQL Class

class ServiceEval(Base):
    __tablename__='serviceEval'
    id=Column(Integer, primary_key=True)
    name=Column(String )
    Eval=Column(String)

#initiate session
Base.metadata.create_all(engine)

Session=sessionmaker(bind=engine)
session=Session()

#declare functions for sql

def NewEntry(namei,evali): 
        nservice=ServiceEval(name=namei, Eval=evali)
        session.add(nservice)
        session.commit()


def GetService(namei):
    return session.query(ServiceEval).filter(ServiceEval.name==namei).first()

def ListService():
    return session.query(ServiceEval).all()


#declare functions for REST

class ServiceEvalManage(Resource):
    def get(self): #list the services
        raw_servicelist=ListService()
        finallist=[]
        for x in raw_servicelist:
            finallist.append(x.name)
            finallist.append(x.Eval)
        return jsonify(finallist)
    def post(self): #creates a evaluation, needs to verify if the service exists
        data=loads(request.data)
        print(data)
        try:
            print(data['name'])
            print(data['Eval'])
            ver=get('http://127.0.0.1:8001/service/{}/'.format(data['name'])).status_code
            print(ver)
            if ver==200:
                print(data)
                status=NewEntry(namei=data['name'], evali=data['Eval'])
                return '',status
            if ver==404:
                return '',400
        except:
            return '',400
        

api.add_resource(ServiceEvalManage,'/')


if __name__=='__main__':
    app.run(host='0.0.0.0',port=8003,debug=True)