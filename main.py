from flask import Flask, redirect, request, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import cgi
import os

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://agent_report:acceptit@localhost:8889/agent_report"
app.config['SQLALCHEMY_ECHO'] = True
app.secret_key = "#decoderring"

db = SQLAlchemy(app)

class Report(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    report = db.Column(db.String(2000))
    agent = db.Column(db.String(120), db.ForeignKey('agent.codename'))

    def __init__(self, title, report, agent):
        self.title = title
        self.report = report
        self.agent = agent

class Agent(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    codename = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    report = db.relationship('Report', backref='Agent')

    def __init__(self, codename, password):
        self.codename = codename
        self.password = password

@app.route("/", methods=["GET", "POST"])
def index():
    reports = Report.query.all()
    return render_template('files.html',reports=reports)

@app.route("/users", methods=["GET"])
def agents():
    agents = Agent.query.all()
    return render_template('agents.html',agents=agents)

@app.route("/profile", methods=["GET"])
def profile():
    user = request.args.get("user")
    reports = Report.query.filter_by(agent=user).all()
    return render_template("files.html",reports=reports)

@app.route("/display", methods=["GET"])
def display():
    id = request.args.get("id")
    report = Report.query.filter_by(id=id).first()
    return render_template("single.html", title=report.title, user=report.agent, report=report.report)

@app.route("/add", methods=["GET","POST"])
def add_report():
    if request.method == "POST":
        title = (request.form["case_title"]).upper()
        if len((title.strip())) == 0:
            flash("ERROR: TITLE REQUIRED","error")
            return render_template("add.html")
        report = request.form["report"]
        if len((report.strip())) == 0:
            flash("ERROR: REPORT REQUIRED","error")
            return render_template("add.html")
        new_report = Report(title,report,session["codename"])
        db.session.add(new_report)
        db.session.commit()
        return redirect("/display?id={}".format(new_report.id))
    else:
        return render_template("add.html")

# LOGIN HANDLERS----------------------------------------------------------------------------------

@app.before_request
def require_login():
    allowed_routes = ['login','register','index','agents','profile','display']
    if request.endpoint not in allowed_routes and 'codename' not in session:
        return render_template("login.html")

@app.route('/login', methods=["GET","POST"])
def login():
    if request.method == "POST":
        codename = (request.form["codename"]).lower()
        password = request.form["pass1"]
        agent = Agent.query.filter_by(codename=codename).first()
        if agent and agent.password == password:
            session['codename'] = codename
            flash("ACCESS GRANTED","success")
            return redirect("/add")
        elif agent and agent.password != password:
            flash("ERROR: CODEPHRASE","error")
            return redirect("/login")
        else:
            flash("ERROR: AGENT DOESN'T EXIST","error")
            return redirect("/login")
    else:
        return render_template("login.html")

@app.route('/logout', methods=['GET'])
def logout():
    del session['codename']
    return redirect('/')

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        codename = (request.form["codename"]).lower()
        if len(codename)<3 or len(codename)>20:
            flash("ERROR: CODENAME", "error")
            return render_template("register.html")
        password = request.form["pass1"]
        passwordv = request.form["pass2"]
        if password != passwordv or (len(password)<3 or len(password)>20):
            flash("ERROR: CODEPHRASE", "error")
            return render_template("register.html")
        existing_agent = Agent.query.filter_by(codename=codename).first()
        if not existing_agent:
            new_agent = Agent(codename,password)
            db.session.add(new_agent)
            db.session.commit()
            session['codename'] = codename
            flash("AGENT ACCEPTED","success")
            return render_template("login.html", codename=codename)
        else:
            flash("ERROR: DOUBLE AGENT","error")
            return render_template("register.html")
    return render_template("register.html")

if __name__ == "__main__":
    app.run()
