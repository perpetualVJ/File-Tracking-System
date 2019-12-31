import os
from flask import Flask, render_template, request,session,url_for,redirect     #importing flask and other functions
import sqlite3
from datetime import datetime
import uuid
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from dateutil.parser import parse
import re
from helpers import login_required, apology

# Configure application
app = Flask(__name__)
app.secret_key = 'your secret key'

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

db = sqlite3.connect('filetracking.db',check_same_thread=False)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

date = datetime.today()      #for date and time
d = date.strftime("%x")

regex = '^[\w\s\.,@\?-]+$'
@app.route("/")
def home():
    session.clear()
    return render_template("home.html")

@app.route("/employee")
def employee():
    session.clear()
    return render_template("employee.html")

@app.route('/emplogin',methods=['POST','GET'])
def emplogin():
        #forget any user email
    if request.method == "POST":
        session.clear()

        c = db.cursor()
        name=request.form['email']
        p =request.form['password']
        if not name or not p:
            return redirect('/employee')
        query = "SELECT * FROM user WHERE emailID = ? AND password = ?"
        h = (name,p)
        c.execute(query,h)
        fetchdata = c.fetchall()
        c.close()
        if len(fetchdata)!= 0 and fetchdata[0][4] == "employee":
            session["user_id"] = fetchdata[0][0]
            session["user"] = "employee"
            return render_template("emlogin.html",emailid = fetchdata[0][0],name = fetchdata[0][2],dep = fetchdata[0][3],post = fetchdata[0][4],date = d)
        else:
            return render_template("oops.html")
    else:
        return redirect("/employee")

@app.route('/adminlogin',methods=['POST'])
def adminlogin():
        session.clear()
        c = db.cursor()
        name=request.form['email']
        p =request.form['password']
        if not name or not p:
            return redirect('/adminlogin')
        query = "SELECT * FROM user WHERE emailID = ? AND password = ?"
        h = (name,p)
        c.execute(query,h)
        fetchdata = c.fetchall()
        c.close()
        if len(fetchdata)!= 0 and fetchdata[0][4] == "admin":
            session["user_id"] = fetchdata[0][0]
            session["user"] = "admin"
            return render_template("alogin.html",emailid = fetchdata[0][0],name = fetchdata[0][2],dep = fetchdata[0][3],post = fetchdata[0][4],date = d)
        else:
            return render_template("oops.html")

@app.route('/uietofficerlogin',methods=['POST'])
def uietofficerlogin():
        session.clear()
        c = db.cursor()
        name=request.form['email']
        p =request.form['password']
        if not name or not p:
            return redirect('/uietofficerlogin')
        query = "SELECT * FROM user WHERE emailID = ? AND password = ?"
        h = (name,p)
        c.execute(query,h)
        fetchdata = c.fetchall()
        c.close()
        if len(fetchdata)!= 0 and fetchdata[0][4] == "officer":
            session["user_id"] = fetchdata[0][0]
            session["user"] = "officer"
            return render_template("ologin.html",emailid = fetchdata[0][0],name = fetchdata[0][2],dep = fetchdata[0][3],post = fetchdata[0][4],date = d)
        else:
            return render_template("oops.html")



@app.route("/submit/<email>",methods=['POST'])
@login_required
def submit(email):
    cc = db.cursor()
    e = email
    s = request.form.get('subject')
    b = request.form.get('body')
    if re.search(regex, s) == None or re.search(regex,b) == None:
        return apology("Enter valid info",400)
    if email == 'officer@gmail.com':
        query = "INSERT INTO file(fileno,subject,body,date,uietacceptance,uietremarks,uietacceptdate) VALUES(?,?,?,?,?,?,?)"
        ll = uuid.uuid4().int
        l = ll % 1000000007
        h = (l,s,b,d,'Accepted','Not Specified',d)
        cc.execute(query,h)
        db.commit()
    else:
        query = "INSERT INTO file(fileno,subject,body,date) VALUES(?,?,?,?)"
        ll = uuid.uuid4().int
        l = ll % 1000000007
        h = (l,s,b,d)
        cc.execute(query,h)
        db.commit()


    query = "INSERT INTO fileuser(fileno,emailID) VALUES(?,?)"
    h = (l,e)
    cc.execute(query,h)
    db.commit()
    return render_template("success.html",number=l)

@app.route("/states")
def status():
    session.clear()
    return render_template("states.html")

@app.route("/statuscheck",methods = ["POST"])
def statuscheck():
    session.clear()
    cc = db.cursor()
    s = request.form.get('file')

    query = "SELECT * FROM file WHERE fileno = ?"
    cc.execute(query,(s,))
    db.commit()
    fetchdata = cc.fetchall()
    if len(fetchdata) == 1:
        return render_template("status.html",fileno = fetchdata[0][0],submit = d,uietstatus = fetchdata[0][4],uietremarks = fetchdata[0][5],adminstatus = fetchdata[0][6],adminremarks = fetchdata[0][7])
    else:
        return render_template("filenotexist.html")

@app.route("/contactus")
def contactus():
    session.clear()
    return render_template("contactus.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/admin")
def admin():
    session.clear()
    return render_template("admin.html")

@app.route("/uietoffice")
def uietoffice():
    session.clear()
    return render_template("uietoffice.html")

@app.route("/upload")
@login_required
def upload():
    email = session["user_id"]
    c = db.cursor()
    #s = request.form.get('email')
    query = "SELECT fileno FROM fileuser WHERE emailID=?"
    c.execute(query,(email,))
    l = []
    db.commit()
    fetchdata = c.fetchall()
    for i in range(0,len(fetchdata)):
        query = "SELECT fileno,date,uietacceptance,uietremarks,adminacceptance,adminremarks FROM file WHERE fileno = ?"
        c.execute(query,(fetchdata[i][0],))
        l.append(list(c.fetchall()[0]))

    if session["user"] == "employee":
        return render_template("eupload.html",fetchdata = l)
    else:
        return render_template("upload.html",fetchdata = l)

@app.route("/officelog")
@login_required
def officelog():
    c = db.cursor()
    query = "SELECT COUNT(*) FROM file WHERE date = ? AND uietremarks != ?"
    c.execute(query,(d,"Not Specified"))
    fetchdata = c.fetchall()
    query = "SELECT COUNT(*) FROM file WHERE uietacceptance = ?"
    c.execute(query,('Pending',))
    pending = c.fetchall()
    query = "SELECT COUNT(*) FROM file WHERE uietacceptance = ? AND uietremarks != ?"
    c.execute(query,('Accepted',"Not Specified"))
    accepted = c.fetchall()
    query = "SELECT COUNT(*) FROM file WHERE uietacceptance = ?"
    c.execute(query,('Rejected',))
    rejected = c.fetchall()

    s = datetime.now()
    smonth = s.month
    syear = s.year
    query = "SELECT date FROM file WHERE uietremarks != ?"
    c.execute(query,("Not Specified",))
    fetch = c.fetchall()
    month = 0
    year = 0
    for i in fetch:
        a = parse(i[0][0])
        if smonth == a.month:
            month = month + 1
        if syear == a.year:
            year = year + 1

    return render_template("uietofficelog.html",today = fetchdata[0][0],pending = pending[0][0],accepted = accepted[0][0],rejected = rejected[0][0],year = year,month = month)

@app.route("/createfile")
@login_required
def createfile():
    if session["user"] == "employee":
        return render_template("ecreatefile.html",emailid = session["user_id"])
    else:
        return render_template("createfile.html",emailid = session["user_id"])

@app.route("/pendingrequests")
@login_required
def pendingrequests():
    email = session["user_id"]
    c = db.cursor()
    query = "SELECT fileno FROM fileuser WHERE emailID != ?"
    c.execute(query,(email,))
    db.commit()
    l = []
    fetchdata = c.fetchall()
    for i in range(0,len(fetchdata)):
        print(fetchdata[i][0])
        query = "SELECT fileno,body,subject,date FROM file WHERE fileno = ? AND uietacceptance = ?"
        c.execute(query,(fetchdata[i][0],'Pending',))
        p=c.fetchall()
        if(len(p)!=0):
            l.append(p[0])
    #print(l)
    return render_template("pendingrequests.html",fetchdata = l)


@app.route("/uietsubmit/<file>",methods=['POST'])
@login_required
def uietsubmit(file):
    c = db.cursor()
    f = file
    a = request.form.get('status')
    b = request.form.get('remarks')

    query = "UPDATE file SET uietacceptance = ?, uietremarks = ?, uietacceptdate = ? WHERE fileno = ?"
    h = (a, b, d, f)
    c.execute(query,h)

    db.commit()
    return redirect(url_for('pendingrequests',emailidd = 'uietofficer@gmail.com'))

@app.route("/adminsubmit/<file>",methods=['POST'])
@login_required
def adminsubmit(file):
    c = db.cursor()
    f = file
    a = request.form.get('status')
    b = request.form.get('remarks')

    query = "UPDATE file SET adminacceptance = ?, adminremarks = ?, adminacceptdate = ? WHERE fileno = ?"
    h = (a, b, d, f)
    c.execute(query,h)

    db.commit()
    return redirect(url_for('adminpendingrequests',emailidd = 'admin@gmail.com'))


@app.route("/adminpendingrequests")
@login_required
def adminpendingrequests():
    emailid = session["user_id"]
    c = db.cursor()
    query = "SELECT fileno FROM fileuser WHERE emailID != ?"
    c.execute(query,(emailid,))
    db.commit()
    l = []
    fetchdata = c.fetchall()
    for i in range(0,len(fetchdata)):
        print(fetchdata[i][0])
        query = "SELECT fileno,body,subject,date FROM file WHERE fileno = ? AND uietacceptance = ? AND adminacceptance = ?"
        c.execute(query,(fetchdata[i][0],'Accepted','Pending',))
        p=c.fetchall()
        print(p)
        if(len(p)!=0):
            l.append(p[0])
    #print(l)
    return render_template("adminpendingrequests.html",fetchdata = l)

@app.route("/adminofficelog")
@login_required
def adminofficelog():
    c = db.cursor()
    query = "SELECT COUNT(*) FROM file WHERE uietacceptdate = ? AND uietacceptance =?"
    c.execute(query,(d,"Accepted"))
    fetchdata = c.fetchall()
    query = "SELECT COUNT(*) FROM file WHERE adminacceptance = ? AND uietacceptance =?"
    c.execute(query,('Pending',"Accepted"))
    pending = c.fetchall()
    query = "SELECT COUNT(*) FROM file WHERE adminacceptance = ? AND uietacceptance =?"
    c.execute(query,('Accepted',"Accepted"))
    accepted = c.fetchall()
    query = "SELECT COUNT(*) FROM file WHERE adminacceptance = ? AND uietacceptance =?"
    c.execute(query,('Rejected',"Accepted"))
    rejected = c.fetchall()

    s = datetime.now()
    smonth = s.month
    syear = s.year
    query = "SELECT date FROM file WHERE uietacceptance =?"
    c.execute(query,("Accepted",))
    fetch = c.fetchall()
    month = 0
    year = 0
    for i in fetch:
        a = parse(i[0][0])
        if smonth == a.month:
            month = month + 1
        if syear == a.year:
            year = year + 1
    return render_template("adminofficelog.html",emailid = session["user_id"],today = fetchdata[0][0],pending = pending[0][0],accepted = accepted[0][0],rejected = rejected[0][0],year = year, month = month)


@app.route("/createnew")
@login_required
def createnew():
    return render_template("createnew.html")

@app.route("/newuser", methods = ['POST'])
@login_required
def newuser():
    n = request.form.get('name')
    e = request.form.get('email')
    p = request.form.get('password')
    d = request.form.get('department')
    po = request.form.get('post')

    r = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'

    if re.search(r,e) == None or re.search("^[a-zA-Z\s]+$",n) == None or re.search("^[\w]+$",d) == None or re.search("^[a-zA-Z]+$",po) == None:
        return apology("Enter valid info",400)
    elif len(p) < 8 or re.search("[\w_/$@]+", p) == None:
        return apology("Choose valid password",400)
    c = db.cursor()

    query = "SELECT * FROM user WHERE emailID = ?"
    c.execute(query,(e,))
    fetchdata = c.fetchall()

    if len(fetchdata) == 0:
        query = "INSERT INTO user(emailID,password,name,department,post) VALUES (?,?,?,?,?)"
        h = (e,p,n,d,po)
        c.execute(query,h)
        db.commit()
        return render_template("usersuccess.html")
    else:
        return render_template("alreadyexist.html")

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

if __name__ == "__main__":
    app.run(debug=True)
