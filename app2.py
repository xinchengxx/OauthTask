from flask import Flask,render_template,request,flash,make_response,jsonify,redirect,session,json
from flask_sqlalchemy import SQLAlchemy
import pymysql
import random,time
import base64
import hmac
import requests
from furl import furl
app = Flask(__name__)



key  = "JD98Dskw=23njQndW9D"#用于加密的key
app.config['SQLALCHEMY_DATABASE_URI']='mysql+pymysql://root:leh20020929@localhost:3306/demo2'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db=SQLAlchemy(app)
app.config['SECRET_KEY']=random._urandom(24) ###对一些hash函数有影响

clients={'demo1':'demo1secret'} ###client_id和client_secret的映射
auth_redirect_uri={'demo1':'http://localhost:5000/demo1/callback'}   #client_id 和 redirect_uri的映射
auth_code={}    ####client_id和授权码的映射
temp_clients=[]
class new_user(db.Model):
    __tablename__='users'
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(16),unique=True)
    passwd=db.Column(db.String(16))

class urls(db.Model):
    __tablename__='urls'
    username=db.Column(db.String(16),unique=True)
    url=db.Column(db.String(50))





def gen_auth_code(client_id):
    code=random.randint(0,10000)
    auth_code[str(code)]=client_id
    return code

def gen_token(uid:str,expire=3600):
    uid_byte=uid.encode('utf-8')
    time_s=str(time.time()+expire) #过期时间
    sh1_str=hmac.new(key.encode('utf-8'),uid_byte,'sha1').hexdigest()
    token=":".join([uid,time_s,sh1_str])  #验证token的合理性
    b64_token = base64.urlsafe_b64encode(token.encode("utf-8"))
    return b64_token.decode("utf-8") #生成token

def verify_token(token):
    token_str=base64.urlsafe_b64decode(token).decode('utf-8')
    token_list = token_str.split(':')
    print(token_list)
    if len(token_list)!=3:
            return False
    uid=token_list[0]
    ts_str = token_list[1]
    if float(ts_str) < time.time():
        # token expired
        return False
    sha1=hmac.new(key.encode('utf-8'),uid.encode('utf-8'),'sha1').hexdigest()
    print(sha1,uid)
    if sha1!=token_list[2]:
        return False
    return True
###生成token的方式

token = gen_token('leh', 3600)
print(token)
print(verify_token(token))

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        username=request.form.get('username')
        password=request.form.get('password')
        if not all([username,password]):
            flash('')
            return '参数输入不正确'
        else:
            user=new_user.query.filter_by(name=username).first()
            if user==None:
                flash('用户名不存在,请注册')
                return render_template('login.html')
            else:
                if user.passwd!=password:
                    return '密码错误'
                else:
                    session[username]=username
                    uri='/%s/home'%(username)
                    return redirect(uri) #登陆成功直接到图床界面
    return render_template('login.html')


@app.route('/<client>/login',methods=['POST','GET'])
def client_login(client):
    client_id='demo1'
    redirect_uri=auth_redirect_uri.get(client_id)
    uri='http://localhost:5000/oauth?response_type=code&client_id=%s'%(client_id)
    return redirect(uri)

@app.route('/oauth',methods=['POST','GET'])
def oauth():
    if request.method=='GET':
        if request.args.get('client_id'):
            if not clients.get(request.args.get('client_id')):
                return 'error'  #如果app没有注册返回error
            else:
                temp_clients.append(request.args.get('client_id'))
                return  render_template('oauth.html')   #返回登陆页面
    else:
        if request.form.get('username'):
            #那么就是注册登陆页面
            username=request.form.get('username')
            pw=request.form.get('password')
            user=new_user.query.filter_by(name=username).first()
            if user.passwd!=pw:
                return 'error'
            else:
            #是选择界面
                val=request.form.get('scope')
                time=request.form.get('time') ###get到的不知道是数字还是字符串
                client_id=temp_clients.pop()
                code = gen_auth_code(client_id)
                redirect_uri=auth_redirect_uri.get(client_id)+'?scope=%s&time=%s&code=%s&user=%s' %(val,time,code,username)
                return redirect(redirect_uri)




#回调的视图函数
@app.route('/<service>/callback',methods=['GET','POST'])
def callback(service):
        scope=request.args.get('scope')
        time=request.args.get('time')
        code=request.args.get('code')
        client_id="demo1"
        client_secret="demo1secret"
        username=request.args.get('user')
        uri='http://localhost:5000/oauth/token'+'?scope=%s&time=%s&code=%s&client_id=%s&client_secret=%s&user=%s'%(scope,time,code,client_id,client_secret,username)
        resp=requests.get(uri)
        print(resp.text)
        uri_='http://localhost:5000/api?user=%s&token=%s&scope=%s'%(username,resp.text,scope)
        return redirect(uri_)




@app.route('/oauth/token',methods=['GET','POST'])
def token():
        code=request.args.get('code')
        client_id=request.args.get('client_id')
        client_secret=request.args.get('client_secret')
        print(client_id,client_secret,code)
        if clients.get(client_id)==client_secret and auth_code.get(code)==client_id:
            time=request.args.get('time')
            user=request.args.get('user')
            return gen_token(user,int(time))
        else:
            return 'error'





@app.route('/register',methods=['GET','POST'])
def register():
    print(request.method)
    if request.method=='POST':
        username=request.form.get('username')
        passwd1=request.form.get('password')
        passwd2=request.form.get('password2')
        if not all([username,passwd2,passwd1]):
            flash('参数不完整')
            return render_template('register.html')
        elif passwd1!=passwd2:
            return '两次密码不一致'
        else:
            user=new_user(name=username,passwd=passwd1)
            db.session.add(user)
            db.session.commit()
            return '注册成功,欢迎你,%s ' %(username)
    else:
        return render_template('register.html')


@app.route('/api',methods=['GET','POST'])
def api():
    username=request.args.get('user')
    token=request.args.get('token')
    if verify_token(token):

        ###这里修改成用户数据
        if request.args.get('scope')=='read':
            return "hello,%s" % (username) #返回用户数据
        else:
            return '图床页面' #返回图床界面，此时相当于用户登陆

    else:
        return 'error'


@app.route('/<user>/home',methods=['GET','POST'])
def home(user):
    #首先是用户的
    if session.get(user)==None:

        return redirect('/login')
    if session[user]==user:
        url1=urls.query.join(new_user,new_user.name==urls.username).filter(urls.username==user)
        dict={}
        for i in url1:
            temp={i.username:i.url}
            dict.update(temp)
        return jsonify({
            "username":user,
            "data":json.dumps(dict)
        })



    ####接下来考虑连接外键和数据库的事情





if __name__=='__main__':
    print('hello')
    db.drop_all()  ###删表
    db.create_all()  ##创建表
    app.run()