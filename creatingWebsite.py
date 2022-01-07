from flask import Flask, render_template, url_for, redirect, request, session, flash
from datetime import timedelta, datetime
import json
import requests
from flask_sqlalchemy import SQLAlchemy
import sqlite3
from creatingChatDataframe import *
import pytz
from geopy.geocoders import Nominatim

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

# Runnning the flask website and user database
app = Flask(__name__)
app.secret_key = "Hello world"
app.permanent_session_lifetime = timedelta(minutes=5)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

database = SQLAlchemy(app)

# Opening a connection to the chat database
connection = sqlite3.connect("chat.sqlite3", check_same_thread=False)
cursor = connection.cursor()

# Setting up a connection to geopy
geolocator = Nominatim(user_agent="weather_website")

class users(database.Model):
    _id = database.Column("id", database.Integer, primary_key=True)
    name = database.Column(database.String(100))
    username = database.Column(database.String(100))
    password = database.Column(database.String(100))
    email = database.Column(database.String(100))
    # bio = database.Column(database.String(100))
    # age = database.Column(database.String(100))

    def __init__(self, name, username, password, email):
        self.name = name
        self.password = password
        self.email = email
        self.username = username
        # self.bio = ""
        # self.age = ""

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

        # add the bio for the sign up page

        found_user = users.query.filter_by(username=usernm).first()
        if found_user:
            flash("This username already exists! Please chose another one.")
            return render_template('signup.html')

        usr = users(nm, usernm, passwrd, None)
        database.session.add(usr)
        database.session.commit()

        session["user"] = usernm, passwrd, nm
        session['email'] = None
        session["texting"] = "",""
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
            session['texting'] = '',''
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
    session.pop("texting", None)
    return redirect(url_for("login"))

# This is a table of all the users in the app
@app.route("/view")
def view():
    return render_template("view.html", values=users.query.all())

# This allows you to search for a particular user in the database
@app.route("/search", methods=["POST","GET"])
def search():
    matchs = []
    if request.method=="POST":  
        if "user" in request.form:
            search = request.form['user']
            match = users.query.filter(users.username.contains(search)).all()
            for i in match:
                matchs.append([i.name, i.username, i.password, i.email])
    return render_template("search.html", content=matchs)


randomUsers = []
@app.route("/RandomUserAPI", methods=["POST", "GET"])
def RandomUserAPI():
    if request.method=="POST":
        if request.form['addUser']=="":
            randomUsers.append(getData())
    return render_template("randomUserAPI.html", content=randomUsers)

@app.route("/texting", methods=["POST", "GET"])
def texting():
    if "user" in session:
        # Get the user that is texted
        if request.method=="POST" and "TextUser" in request.form:
            textee = request.form['TextUser'][5:]
            nmee = users.query.filter_by(username=textee).all()[0].name
            session['texting'] = textee, nmee
        if session['texting'][0]=="":
            flash("You need to use this page to text someone !")
            return redirect(url_for("search"))
        elif session['texting'][0]==session['user'][0]:
            flash("You can not text yourself, click here to text !")
            return redirect(url_for("search"))

        # Get the user that is texting
        texter, __ , nm = session["user"]
        first = session['texting'][0] if texter>session['texting'][0] else texter
        second = texter if texter>session['texting'][0] else session['texting'][0]

        chatName = f"text{first}{second}"
        texts = []
        if chatExist(cursor, chatName):
            # Get the existing texts from the dataframe
            texts = getChatInfo(cursor, chatName)
        else:
            # Create table for these texts
            createChat(cursor, chatName)

        # User sends a text, we add it to the text list of dictionaries and to the tables
        if request.method=="POST" and "text" in request.form:
            if request.form['text']!="":
                getPostText(cursor, connection, chatName, texts, texter, request)
        
        # Reverse the texts so they appear in the right order
        texts.reverse()

        return render_template("texting.html", texts = texts, user=texter)
    else:
        flash("You are not logged in and thus cannot text !")
        return redirect(url_for("login"))

@app.route('/weather', methods=["POST", "GET"])
def weather():
    location = "Nothing"
    if request.method=="POST":
        location = request.form['coordinates']
        location = geolocator.geocode(location)

        if location==None:
            flash("Enter a clear location in the form of coordinates, address, city names, etc...")
            return render_template("weather.html", content='Nothing')

    key = 'ae5ecbfb6415d10cddcea23972e386ac'
    lat = location.raw['lat']
    lon = location.raw['lon']

    url = f"https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&appid={key}&units=metric"

    data = requests.get(url).json()
    content = []

    for hourly in data["hourly"]:
        timeStamp = datetime.datetime.fromtimestamp(hourly['dt'], pytz.timezone(data["timezone"])).strftime("%d/%m/%Y %H:%M")
        text = [timeStamp,hourly['weather'][0]['description'].capitalize(),str(hourly['temp'])+"°C", str(hourly['feels_like'])+"°C",str(hourly['wind_speed']) +"m/s",str(hourly['humidity'])+"%"]
        img_url = f"http://openweathermap.org/img/wn/{hourly['weather'][0]['icon']}@2x.png"
        content.append([text, img_url])

    return render_template("weather.html", content=content, location=location.address)

database.create_all()
app.run(debug=True)
