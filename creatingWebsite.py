from flask import Flask, render_template, url_for, redirect, request, session, flash
from datetime import timedelta
import json
import requests
from flask_sqlalchemy import SQLAlchemy

def getValues(dictionary):
	data_keys =["",""]
	for k in dictionary.keys():
		if type(dictionary[k])==dict:
			temp = getValues(dictionary[k])
			data_keys[0]+= temp[0]
			data_keys[1]+= temp[1]
		else:
			data_keys[0]+= "_"+str(dictionary[k])
			data_keys[1]+="_"+str(k)
	return data_keys

def getData():
	data = requests.get("https://randomuser.me/api").json()

	data, keys = getValues(data['results'][0])
	data = data.split("_")
	keys = keys.split("_")

	data = list(zip(keys, data))
	data = [": ".join(x) for x in data]

	del data[0], data[12:14], data[13:20], data[15:17], data[17:19], data[18:20]

	text =  "\n".join(data)
	return text, data[17].split()[1]

#Runnning the flask website
app = Flask(__name__)
app.secret_key = "Hello world"
app.permanent_session_lifetime = timedelta(minutes=5)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

database = SQLAlchemy(app)

class users(database.Model):
	_id = database.Column("id", database.Integer, primary_key=True)
	name = database.Column(database.String(100))
	username = database.Column(database.String(100))
	password = database.Column(database.String(100))
	email = database.Column(database.String(100))

	def __init__(self, name, username, password, email):
		self.name = name
		self.password = password
		self.email = email
		self.username = username

@app.route("/")
def home():
	return render_template("home.html")

@app.route("/signup", methods=["POST", "GET"])
def signup():
	if request.method=="POST":
		session.permanent = True
		usernm = request.form['usernm']
		passwrd = request.form['passwrd']
		nm = request.form['nm']

		found_user = users.query.filter_by(username=usernm).first()
		if found_user:
			flash("This username already exists! Please chose another one.")
			return render_template('signup.html')

		usr = users(nm, usernm, passwrd, None)
		database.session.add(usr)
		database.session.commit()

		session["user"] = usernm, passwrd, nm
		session['email'] = None
		flash(f"Signed up successfully, {nm} !", "info")
		return redirect(url_for("user"))

	if "user" in session:
		flash("You are already logged in")
		return redirect(url_for("user"))

	return render_template("signup.html")

@app.route("/login", methods=["POST", "GET"])
def login():
	if request.method == "POST":
		session.permanent = True
		usernm = request.form["usrnm"]
		password = request.form["passwrd"]

		found_user = users.query.filter_by(username=usernm, password = password).first()
		if found_user:
			session["user"] = usernm, password, found_user.name
			session['email'] = found_user.email
			flash(f"Logged successfully, {found_user.name} !", "info")
			return redirect(url_for("user"))
		else:
			flash("The username or password you entered are not connected to an account !")
			return render_template("login.html")
	else:
		if "user" in session:
			flash("You are already logged in")
			return redirect(url_for("user"))
		return render_template("login.html")

@app.route("/user", methods=["POST","GET"])
def user():
	email = None
	if "user" in session:
		usernm, passwd, nm = session["user"]
		if request.method=='POST':
			if "email" in request.form:
				email = request.form['email']
				session['email'] = email
				found_user = users.query.filter_by(name=nm, username = usernm, password=passwd).first()
				found_user.email = email
				database.session.commit()
				flash("Email was saved !")
			if "logout" in request.form:
				return logout()
		else:
			if "email" in session:
				email = session["email"]
		return render_template("user.html", name=nm, username = usernm, password=passwd, email=email)
	else:
		flash("You are not logged in!")
		return redirect(url_for("login"))

@app.route("/logout")
def logout():
	if "user" in session:
		user=session["user"]
		flash(f"You have been logged out, {user[0]}", "info")
	else:
		flash("You are not logged in !")
	session.pop("user", None)
	session.pop("email", None)
	return redirect(url_for("login"))

@app.route("/view")
def view():
	return render_template("view.html", values=users.query.all())

randomUsers = []
@app.route("/RandomUserAPI", methods=["POST", "GET"])
def RandomUserAPI():
	if request.method=="POST":
		print(request.form)
		if request.form['addUser']=="":
			randomUsers.append(getData())
	return render_template("randomUserAPI.html", content=randomUsers)

database.create_all()
app.run(debug=True)