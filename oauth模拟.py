from flask import Flask,request,redirect
import time,random,base64
app=Flask(__name__)
users={
    'magigo':['123456']
}
redirect_uri='http://localhost:5000/client/passport'
client_id='123456'
users[client_id]=[]
auth_code={}
oauth_redirect_uri=[]

def gen_token(uid):
    token=base64.b64encode(':'.join(str[uid],str(random.random()),str(time.time())+7200))
    users[uid].append(token)
    return token

def gen_auth_code(uri):
    code=random.randint(0,10000)
    auth_code[code]=uri
    return code

def verify_token(token):
    _token=base64.b64decode(token)
    if not users.get(_token.split(':')[0])[-1]==token:
            return -1
    if float(_token.split(':')[-1])>=time.time():
            return 1
    else:
            return 0

@app.route('/index',methods=['POST','GET'])
def index():
    print(request.headers)
    return 'hello'

@app.route('/login',methods=['POST','GET'])
def login():
    uid,pw=base64.b64decode(request.headers['Authorization'].split('')[-1]).split(':')
    if users.get(uid)[0]==pw:
        return gen_token(uid)
    else:
        return 'error'

@app.route('/client/login',methods=['POST','GET'])
def client_login():
    uri='http://localhost:5000/oauth?response_type=code&client_id=%s&redirect_uri=%s'%(client_id,redirect_uri)
    return redirect(uri)

@app.route('/oauth',methods=['GET','POST'])
def oauth():
    if request.args.get('user'):
        # print(users.get(request.args.get('user'))[0])
        # print(request.args.get('pw'))
        # if users.get(request.args.get('user'))[0]==int(request.args.get('pw')) :
        #     print('hello')
            uri=oauth_redirect_uri[0]+'?code=%s'%gen_auth_code(oauth_redirect_uri[0])
            print(uri)
            return redirect(uri)
    if request.args.get('code'):
        if auth_code.get(int(request.args.get('code')))==request.args.get('redirect_uri'):
            return 'token'
    if request.args.get("redirect_uri"):
            oauth_redirect_uri.append(request.args.get('redirect_uri'))
            return 'pleaselogin'

@app.route('/test1',methods=['POST','GET'])
def test():
    token=request.args.get('token')
    print(token)
    if token=='token':
        return 'data'
    else:
        return 'error'

@app.route('/client/passport',methods=['POST','GET'])
def client_passport():
    code=request.args.get('code')
    uri='http://localhost:5000/oauth?grant_type=authorization_code&code=%s&redirect_uri=%s&client_id=%s'%(code,redirect_uri,client_id)
    return redirect(uri)


if __name__=='__main__':
    app.run()