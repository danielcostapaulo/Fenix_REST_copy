from flask import Flask,request,make_response
from requests import get,post,delete
from flask.json import jsonify
from flask_restful import Resource,Api
from flask_cors import CORS,cross_origin
import json

#Proxy!

#initialize app

app=Flask(__name__)
api=Api(app)
cors=CORS(app,resources={r"/*": {"origins": '*'}})
#declare functions for REST

class CreateService(Resource): #redirects to the PSDB
    def get(self):
        service_list=get('http://0.0.0.0:8002/').json()
        return make_response(jsonify(service_list),200,{'Access-Control-Allow-Origin': "*"})
    def post(self):
        status=(post('http://0.0.0.0:8002/',data=request.data,headers=request.headers)).status_code
        return '',status

class VerifyService(Resource): #verifies if a service exists
    def get(self,service_name):
        status=get('http://0.0.0.0:8002/{}/'.format(service_name)).status_code
        return '',status
    def delete(self,service_name):
        status=delete('http://0.0.0.0:8002/{}/'.format(service_name)).status_code
        return '',status

class CreateServiceEval(Resource):
    def get(self):
        eval_list=get('http://0.0.0.0:8003/').json()
        return make_response(jsonify(eval_list),200,{'Access-Control-Allow-Origin': "*"})
    def post(self):
        status=(post('http://0.0.0.0:8003/',data=request.data,headers=request.headers)).status_code
        return '',status

class CreateCourse(Resource):
    def get(self):
        course_list=get('http://0.0.0.0:8004/').json()
        return make_response(jsonify(course_list),200,{'Access-Control-Allow-Origin': "*"})
    def post(self):
        status=(post('http://0.0.0.0:8004/',data=request.data,headers=request.headers)).status_code
        return '',status

class GetCourse(Resource):
    def get(self,course_name):
        status=get('http://0.0.0.0:8004/{}/'.format(course_name)).status_code
        return '',status

class GetCourseFromST(Resource):
    def get(self,course_name,st_id):
        status=get('http://0.0.0.0:8004/{}/{}/'.format(st_id,course_name)).status_code
        return '',status
    
class CreateActivity(Resource):
    def get(self):
        activity_list=get('http://0.0.0.0:8005/').json()
        return make_response(jsonify(activity_list),200,{'Access-Control-Allow-Origin': "*"})
    def post(self):
        status=(post('http://0.0.0.0:8005/',data=request.data,headers=request.headers)).status_code
        return '',status

class ActivitiesFromStudent(Resource):
    def get(self,student_id):
        activity_list=get('http://0.0.0.0:8005/{}/'.format(student_id)).json()
        return make_response(jsonify(activity_list),200,{'Access-Control-Allow-Origin': "*"})



api.add_resource(CreateService,'/service/')
api.add_resource(VerifyService,'/service/<service_name>/')
api.add_resource(CreateActivity,'/activity/')
api.add_resource(ActivitiesFromStudent,'/activity/<student_id>/')
api.add_resource(CreateServiceEval, '/eval/')
api.add_resource(CreateCourse, '/course/')  
api.add_resource(GetCourse,'/course/<course_name>/')
api.add_resource(GetCourseFromST,'/course/<st_id>/<course_name>/')

if __name__=='__main__':
    app.run(host='0.0.0.0',port=8001,debug=True)