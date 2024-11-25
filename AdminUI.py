import stat
from flask import Flask, render_template,request, url_for,redirect
from requests import get,post,delete
from json import loads

#admin website!

#The ports are: 8000-adminWS/8001:proxy/8002:PSDB/8003:PSEDB/8004:UCDB/8005:ARDB

app=Flask(__name__)

@app.route('/',methods=['GET'])
def mainpage():
    return render_template("mainpageA.html")

@app.route('/services/',methods=['POST','GET','DELETE'])
def services():
    if request.method=='GET':
        servicelist=get('http://0.0.0.0:8001/service/').json()
        return render_template("servicesA.html",list=servicelist)
    if request.method=='POST':
        service_name=request.form.get('service_name')
        service_name=service_name.strip() #we dont want spaces and paragrafs, so we remove those
        service_name=service_name.replace("\n","")
        service=dict()
        service['name']=service_name
        status=post('http://0.0.0.0:8001/service/',json=service).status_code
        if status==200:
            return render_template("mainpageA.html",mensage="Service sucesefully created")
        else: #the status here should be 400
            return render_template("mainpageA.html",mensage="Service already exists")
    if request.method=='DELETE':
        service_name=loads(request.data)
        status=delete('http://0.0.0.0:8001/service/{}/'.format(service_name)).status_code
        return '',status


@app.route('/serviceeval/',methods=['GET'])
def eval():
    if request.method=='GET':
        servicelist=get('http://0.0.0.0:8001/service/').json()
        return render_template("serviceevallist.html",list=servicelist)

@app.route('/eval<string:service>', methods=['GET'])
def listeval(service):
    servicelist=get('http://0.0.0.0:8001/service/').json()
    if service not in (servicelist):
        return render_template("mainpageA.html",mensage="Service does not exist")
    else:
        serviceevallist=get('http://0.0.0.0:8001/eval/').json()
        lenn=len(serviceevallist)
        count=[0,0,0,0,0,0]
        for i in range (lenn):
            if serviceevallist[i]==service or serviceevallist[i]==service.lower():
                count[int(serviceevallist[i+1])]=count[int(serviceevallist[i+1])]+1
        return render_template("serviceeval.html",list=count, servicee=service)

@app.route('/courses/',methods=['GET'])
def courses():
    if request.method=='GET':
        courselist=get('http://0.0.0.0:8001/course/').json()
        lenn=len(courselist)
        courses=[]
        for i in range (lenn):
            if courselist[i-1] not in courses and i%2==1:
                courses.append(courselist[i-1])
                
        return render_template("courselist.html",list=courses)
    
@app.route('/atd<string:course>', methods=['GET'])
def listatd(course):
    servicelist=get('http://0.0.0.0:8001/course/').json()
    if course not in (servicelist):
        return render_template("mainpageA.html",mensage="Course does not exist")
    else:
        courselist=get('http://0.0.0.0:8001/course/').json()
        lenn=len(courselist)
        atd=[]
        for i in range (1,lenn,2):
            if courselist[i]!="0" and courselist[i-1]==course:
                atd.append(courselist[i])
        return render_template("courseatd.html",list=atd, servicee=course)

@app.route('/activities/',methods=['POST','GET'])
def activities():
    if request.method=='GET':
        return render_template("ActivitiesA.html")
    if request.method=='POST':
        student_id=request.form.get('student_id')
        student_id=student_id.strip() #we dont want spaces and paragrafs, so we remove those
        student_id=student_id.replace("\n","")
        activitylist=get('http://0.0.0.0:8001/activity/{}/'.format(student_id)).json()
        return render_template("ActivitiesA.html",studentlist=activitylist)

if __name__=='__main__':
    app.run(host='0.0.0.0',port=8000,debug=True)