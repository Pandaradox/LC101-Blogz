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
    agent = db.Column(db.Integer, db.ForeignKey('agent.id'))

    def __init__(self, title, report, agent):
        self.title = title
        self.report = report
        self.agent = agent

class Agent(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    report = "db.relationship('Report', backref='agent')"

    def __init__(self, email, password):
        self.email = email
        self.password = password


@app.route("/", methods=["GET", "POST"])
def index():
    session["email"]="jacardarella@gmail.com"
    owner = Agent.query.filter_by(email=session["email"]).first()
    # if request.method == "POST":
    #     title = request.form["case_title"]
    #     report = str(request.form["report"])
    #     new_report = Report(title,report,owner.id)
    #     db.session.add(new_report)
    #     db.session.commit()
    reports = Report.query.filter_by(agent=owner.id).all()
    # done_missions = Mission.query.filter_by(done=True,owner=owner.id).all()
    return render_template('files.html',reports=reports)

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
        new_report = Report(title,report,(Agent.query.filter_by(email=session["email"]).first()).id)
        db.session.add(new_report)
        db.session.commit()
        return redirect("/display?id={}".format(new_report.id))
    else:
        return render_template("add.html")

@app.route("/display", methods=["GET"])
def display():
    id = request.args.get("id")
    report = Report.query.filter_by(id=id).first()
    return render_template("single.html", title=report.title, report=report.report)

# @app.route('/delete-mission', methods=['POST'])
# def delete_task():
#
#     mission_id = int(request.form['mission-id'])
#     mission = Mission.query.get(mission_id)
#     mission.done = True
#     db.session.add(mission)
#     db.session.commit()
#
#     return redirect('/')
#
# @app.before_request
# def require_login():
#     allowed_routes = ['login', 'register']
#     if request.endpoint not in allowed_routes and 'email' not in session:
#         return render_template("login.html", Title="Agent Terminal")
#
# @app.route('/login', methods=["GET","POST"])
# def login():
#     if request.method == "POST":
#         email = (request.form["email"]).lower()
#         password = request.form["pass1"]
#         agent = Agent.query.filter_by(email=email).first()
#         if agent and agent.password == password:
#             session['email'] = email
#             flash("ACCESS GRANTED","success")
#             return redirect("/")
#         else:
#             flash('ACCESS DENIED',"error")
#             return redirect("/login")
#     else:
#         return render_template("login.html", Title="Agent Terminal")
#
# @app.route('/logout', methods=['GET'])
# def logout():
#     del session['email']
#     return redirect('/')
#
# @app.route("/register", methods=["GET","POST"])
# def register():
#     if request.method == "POST":
#         email = (request.form["email"]).lower()
#         password = request.form["pass1"]
#         passwordv = request.form["pass2"]
#         if password != passwordv or (len(password)<3 or len(password) >20):
#             flash("ERROR: CODEPHRASE", "error")
#             return render_template("register.html", Title="Agent Registration")
#         existing_agent = Agent.query.filter_by(email=email).first()
#         if not existing_agent:
#             new_agent = Agent(email,password)
#             db.session.add(new_agent)
#             db.session.commit()
#             session['email'] = email
#             flash("Agent Accepted","success")
#             return render_template("login.html", Title="Agent Terminal", email=email)
#         else:
#             flash("ERROR: DOUBLE AGENT","error")
#             return render_template("register.html", Title="Agent Registration")
#     return render_template("register.html", Title="Agent Registration")

if __name__ == "__main__":
    app.run()
