from flask import Flask,render_template,request,flash
from flask_sqlalchemy import SQLAlchemy
import pymysql
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI']='mysql+pymysql://root:leh20020929@localhost:3306/demo2'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db=SQLAlchemy(app)
#继承子db.Model表示数据库模型
# class Role(db.Model):
#     #定义表和字段
#     __tablename__='roles'
#     id=db.Column(db.Integer,primary_key=True)
#     name=db.Column(db.String(16),unique=True)#表示是一个字段
#     ##关联操作
#     # users=db.relationship('Users')##表示和User模型发生关联，增加了一个users属性
#     users=db.relationship('Users',backref='role') ##表是role是users要用的一个属性，但定义在这边，bcakref表示反引用
#     ##repr()方法显示一个可读字符串
#     def __repr__(self):
#         return '<Role:%s %s>' %(self.name,self.id)
#
#
# class Users(db.Model):
#     __tablname__='users'
#     id=db.Column(db.Integer,primary_key=True)
#     name=db.Column(db.String(16),unique=True)
#     role_id=db.Column(db.Integer,db.ForeignKey('roles.id')) #表名外键
#     #Users希望有一个role属性，但是这个属性的定义需要在另一个模型中定义
#     password=db.Column(db.String(32))
#     email=db.Column(db.String(32))
#     def __repr__(self):
#         return '<User: %s %s %s %s>' %(self.name,self.id,self.email,self.password)
# ##增删改，

class new_user(db.Model):
    __tablename__='users'
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(16),unique=True)
    passwd=db.Column(db.String(16))



@app.route('/register/',methods=['GET','POST'])
def register():
    print(request.method)
    if request.method=='POST':
        username=request.form.get('username')
        passwd1=request.form.get('password')
        passwd2=request.form.get('password2')
        if not all([username,passwd2,passwd1]):
            flash('参数不完整')
        elif passwd1!=passwd2:
            return '两次密码不一致'
        else:
            user=new_user(name=username,passwd=passwd1)
            db.session.add(user)
            db.session.commit()
            return '注册成功,欢迎你,%s ' %(username)
    else:
        return render_template('register.html')


@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        username=request.form.get('username')
        password=request.form.get('password')
        if not all([username,password]):
            return '参数输入不正确'
        else:
            user=new_user.query.filter_by(name=username).first()
            if user==None:
                return '用户名不存在，请注册'
            else:
                if user.passwd!=password:
                    return '密码错误'
                else:
                    return '登陆成功'
    return render_template('login.html')



if __name__ == '__main__':
    print('hello')
    # db.drop_all()  ###删表
    db.create_all()  ##创建表
    app.run()