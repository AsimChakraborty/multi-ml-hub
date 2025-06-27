from flask import Flask, render_template, request,url_for,redirect
import numpy as np
import pickle

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin,login_user,login_required,LoginManager,logout_user,current_user
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField
from wtforms.validators import InputRequired,Length,ValidationError
from flask_bcrypt import Bcrypt



app = Flask(__name__)
db=SQLAlchemy(app)
bcrypt= Bcrypt(app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/our_user'


app.config['SECRET_KEY'] = "random string"

login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view="login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model,UserMixin):
   id = db.Column( db.Integer, primary_key = True)
   username = db.Column(db.String(20),nullable=False,unique=True)
   password = db.Column(db.String(20),nullable=False)
   

class RegisterForm(FlaskForm):
    username=StringField(validators=[InputRequired(),Length(min=4,max=20)],render_kw={"placeholder":"Username"})
    password=PasswordField(validators=[InputRequired(),Length(min=4,max=20)],render_kw={"placeholder":"password"})
    submit=SubmitField("Register")


def validate_username(self,username):
    existing_user_username=User.query.filter_by(username=username.data).first()

    if existing_user_username:
        raise ValidationError("The username already exixts.please choose a different one")



class LoginForm(FlaskForm):
    username=StringField(validators=[InputRequired(),Length(min=4,max=20)],render_kw={"placeholder":"Username"})
    password=PasswordField(validators=[InputRequired(),Length(min=4,max=20)],render_kw={"placeholder":"password"})
    submit=SubmitField("Login")


## Load the model
try:
    with open('trained_model.sav', 'rb') as file:
        model = pickle.load(file)
except EOFError:
    print("The file is empty or does not exist. Please make sure the file exists and has data in it.")
except Exception as e:
    print(f"An error occurred: {e}")  
else:
    # code that uses the model only if it was successfully loaded
    print(model) 

@app.route('/',methods=['GET'])
def Home():
    return render_template('index.html')

@app.route("/predict", methods=['POST'])
def predict():
    if request.method == 'POST':
        age = float(request.form['age'])
        Gender = request.form['sex']
        if (Gender == 'male'):
            Gender = 0
        else:
            Gender = 1
        currentSmoker = float(request.form['currentSmoker'])
        cigsPerDay = float(request.form['cigsPerDay'])
        BPMeds = float(request.form['BPMeds'])
        prevalentStroke = float(request.form['prevalentStroke'])
        prevalentHyp = float(request.form['prevalentHyp'])
        diabetes = float(request.form['diabetes'])
        totChol = float(request.form['totChol'])
        sysBP = float(request.form['sysBP'])
        diaBP = float(request.form['diaBP'])
        BMI = float(request.form['BMI'])
        heartRate = float(request.form['heartRate'])
        glucose = float(request.form['glucose'])
  
        values = np.array([[Gender,age,currentSmoker,cigsPerDay,BPMeds,prevalentStroke,prevalentHyp,diabetes,totChol,sysBP,diaBP,BMI,heartRate,glucose]])
        prediction = model.predict(values)
        prediction = round(prediction[0],2)
        if (prediction == 0):
            prediction_text = 'You have no Heart Disease'
        else:
            prediction_text = 'You have Heart Disease'
       
        return render_template('dashboard.html', prediction_text=prediction_text)



@app.route('/home')
def home():
    return render_template('home.html')
 

@app.route('/login',methods=['GET','POST'])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        user=User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password,form.password.data):
                load_user(0)
                return redirect (url_for('Home'))

    return render_template("login.html",form=form)


@app.route("/register",methods=['GET','POST'])
def register():
    form=RegisterForm()

    if form.validate_on_submit():
       hashed_password=bcrypt.generate_password_hash(form.password.data)
       new_user=User(username=form.username.data,password=hashed_password) 
       db.session.add(new_user)
       db.session.commit()
       return redirect(url_for('login'))
    

    return render_template('register.html',form=form)

@app.route('/dashboard',methods=['GET','POST']) 
@login_required  
def dashboard():
    return render_template("dashboard.html")

@app.route('/logout',methods=['GET','POST']) 
@login_required
def logout():
    load_user()
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True)