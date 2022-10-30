from flask import Flask, request, render_template, redirect, url_for
import psycopg2
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import requests
app = Flask(__name__)
app.config['SECRET_KEY'] = 'Thisissecretmyfriendo!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/madi/pythondbms4.db'
Bootstrap(app)
bd = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(bd.Model):
    id = bd.Column(bd.Integer, primary_key=True)
    username = bd.Column(bd.String(15), unique=True)
    email = bd.Column(bd.String(50), unique=True)
    password = bd.Column(bd.String(80))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')
class RegisterForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def form_example():
    if request.method == 'POST':
        address=request.form.get('address')
        url = 'https://solana-gateway.moralis.io/nft/mainnet/' + address + '/metadata'
        headers = {
            "accept": "application/json",
            "X-API-Key": "iWXzBLaUXSfgBOJ5y8lmb9h5xAstww6nm2wkDTXOxsL1vLeoANc8njHGpnTrQWcM"
        }
        response = requests.get(url, headers=headers)
        print(response.text)
        conn = psycopg2.connect(
        database="pythonass4(nft)", user='postgres', password='1503', host='127.0.0.1', port='5432'
        )
        cursor = conn.cursor()
        create_script = ''' CREATE TABLE IF NOT EXISTS NFT
(
  name VARCHAR(200),
  address VARCHAR(1000))'''  
        cursor.execute(create_script) 
        insert_script = "INSERT INTO NFT (name, address) VALUES (%s, %s)"
        insert_value = ("NFT name", response.text)
        cursor.execute(insert_script, insert_value) 
        conn.commit()
        conn.close()
        return '''
                  <h1>The information about nft: {}</h1>'''.format(response.text)
    return '''
           <form method="POST">
               <div><label>address: <input type="text" name="address"></label></div>
               <input type="submit" value="Get Info">
           </form>'''

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('dashboard'))
        return '<h1>Invalid username or password</h1>'
    return render_template('Login.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        bd.session.add(new_user)
        bd.session.commit()
        return '<h1>New user has been created!</h1>'
    return render_template('signup.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)