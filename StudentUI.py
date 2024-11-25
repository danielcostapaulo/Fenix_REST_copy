import json
from urllib.parse import uses_relative
from flask import Flask, jsonify, render_template,request,session,redirect, url_for
from flask_login import LoginManager,UserMixin,login_user,logout_user,login_required,current_user
from requests import get,post
from requests_oauthlib import OAuth2Session
import os

app=Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)

client_id="ID"
client_secret="SECRET"

class User:
    def __init__(self,id):
        self.id=id
    def to_json(self):
        return {"id":self.id}
    def is_authenticated(self):
        return True

    def is_active(self):   
        return True           

    def is_anonymous(self):
        return False          

    def get_id(self):         
        return self.id

@login_manager.user_loader
def load_user(user_id):
    if user_id in session:
        user=User(id=session[user_id]['id'])
        return user
    else:
        return None

@login_manager.unauthorized_handler
def unauthorized():
    return redirect('/')

@app.route("/")
def index():
    #makes sure its on smartphone and get auth_url
    user_agent = request.headers.get('User-Agent')
    user_agent = user_agent.lower()
    # if "android" in user_agent or "iphone" in user_agent:
    if True:
        redirect_url=request.base_url+'callback'
        authorization_base_url='https://fenix.tecnico.ulisboa.pt/oauth/userdialog?client_id={}&redirect_uri={}'.format(client_id,redirect_url)
        fenix=OAuth2Session(client_id)
        authorization_url,state=fenix.authorization_url(authorization_base_url)
        session['oauth_state']=state
        return redirect(authorization_url)
    else:
        return "The Student interface should be only throught a smartphone"

@app.route("/callback",methods=["GET"])
def callback():
    #logs into fenix
    code=request.args.get('code')
    redirect_url=request.base_url
    token_url='https://fenix.tecnico.ulisboa.pt/oauth/access_token?client_id={}&client_secret={}&redirect_uri={}&code={}&grant_type=authorization_code'.format(client_id,client_secret,redirect_url,code)
    fenix=OAuth2Session(client_id,state=session['oauth_state'])
    token=fenix.fetch_token(token_url,client_secret=client_secret,authorization_response=request.url)
    session['ouath_token']=token
    #get user name
    user_info=fenix.get('https://fenix.tecnico.ulisboa.pt/api/fenix/v1/person').json()
    user=User(user_info['username'])
    session[user.id]=user.to_json()
    login_user(user)
    #get users UC
    UC_list=get('http://0.0.0.0:8001/course/').json()
    if (user.id in UC_list)==False: #means that the users courses havent been registered in the DB yet
        user_UC=fenix.get(' https://fenix.tecnico.ulisboa.pt/api/fenix/v1/person/courses').json()
        for uc in user_UC['attending']:
            #for each UC there will be a new entry at the UCDB
            mensage=dict()
            mensage={"course":uc['acronym'],"st_id": user.id}
            mensagejson=json.dumps(mensage,default=str)
            post('http://0.0.0.0:8001/course/',data=mensagejson)
    return redirect(url_for('.input'))

@app.route("/input",methods=["GET"])
@login_required
def input():
    user_id=current_user.id
    UC_list=get('http://127.0.0.1:8001/course/').json()
    courseList=[]
    for i in range(1,len(UC_list),2):
        if user_id==UC_list[i]:
            courseList.append(UC_list[i-1])
    Service_list=get('http://127.0.0.1:8001/service/').json()
            
    return render_template("input.html", student_id=user_id,course=courseList,service=Service_list)

if __name__=="__main__":
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = "1"

    app.secret_key = os.urandom(24)
    app.run(host='0.0.0.0',port=8006,debug=True)