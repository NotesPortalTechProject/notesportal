from flask import Flask,render_template,redirect,send_file,request,jsonify
import mysql.connector,random,string,json
from datetime import datetime
from werkzeug.utils import secure_filename
from docx2pdf import convert
from pathlib import Path
from mailsend import sendmail

app  = Flask(__name__)
favoritelist = []
data = ""
navsub = []

@app.route("/",methods=["GET","POST"])
def index():
    mydb = mysql.connector.connect(host="localhost",user="root",password="",database="notesportal")
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM users")
    userslst = mycursor.fetchall()
    id = "".join(random.sample(string.hexdigits,6))
    firstname = ""
    lastname = ""
    username = ""
    mail = ""
    num = 0
    flag = 0
    subjectlst = []
    if request.method == "POST":
        firstname = request.form["firstname"]
        lastname = request.form["lastname"]
        username = request.form["username"]
        mail = request.form["email"]
        num = int(request.form["numsub"])
        for user in userslst:
            if user[3] == username:
                flag+=1
        if flag == 0:
            try:
                for x in range(num):
                    subjectlst.append(request.form[f"subject_{x}"].upper())
                query = "insert into users (id,firstname,lastname,username,email,subjects) values (%s,%s,%s,%s,%s,%s)"
                mycursor.executemany(query,[(id,firstname,lastname,username,mail,str(subjectlst))])
                sendmail(username,mail=mail)
                mydb.commit()
                navtemplst = [id,firstname,lastname,username,mail,str(subjectlst)]
                for x in range(5):
                    navsub[x] = navtemplst[x]
                return redirect("/home")
            except KeyError:
                pass
        else:
            print("User Already Exists")
            return redirect("/signin")
    mycursor.close() 
    return render_template("index.html",num=num,firstname=firstname,lastname=lastname,username=username,mail=mail)

@app.route("/home",methods=["POST","GET"])
def home():
    global navsub
    global data
    mydb = mysql.connector.connect(host="localhost",user="root",password="",database="notesportal")
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM users")
    userslst = mycursor.fetchall()
    print(navsub)
    username = navsub[3]
    for user in userslst:
            if user[3] == username:
                navsub = user
    datalist = []
    if request.method == "POST":
        mydb = mysql.connector.connect(host="localhost",user="root",password="",database="notesportal")
        mycursor = mydb.cursor()
        try:
            data = request.form["navbarsubject"]
        except KeyError:
            pass
        mycursor.execute("SELECT * FROM notes")
        fetchdata = mycursor.fetchall()
        for element in fetchdata:
            if data == element[3] and data != "":
                eledict = {}
                eledict["id"] = element[0]
                eledict["date"] = element[1]
                eledict["filename"] = element[2]
                eledict["subjectname"] = element[3]
                eledict["filetype"] = element[4]
                eledict["filelink"] = element[5]
                print("found")
                datalist.append(eledict)
        choosefile = request.form.get("pdfbutton")
        if choosefile:
            choosefile = choosefile.replace("\'","\"")
            choosefile = json.loads(choosefile)
            return send_file(choosefile["filelink"],download_name=choosefile["filename"],as_attachment=True)
        favorite = request.form.get("favorite")
        if favorite and favorite not in str(favoritelist):
            favorite = favorite.replace("\'","\"")
            favorite = json.loads(favorite)
            favoritelist.append(favorite)
        elif favorite and (favorite in str(favoritelist)):
            favorite = favorite.replace("\'","\"")
            favorite = json.loads(favorite)
            favoritelist.remove(favorite)
        mycursor.close()
    return render_template("home.html",navsublst=eval(navsub[5]),pdflist=datalist,favoritelist=favoritelist)

@app.route("/upload",methods=["POST","GET"])
def upload():
    mydb = mysql.connector.connect(host="localhost",user="root",password="",database="notesportal")
    mycursor = mydb.cursor()
    if request.method == "POST":
        file = request.files["file"]
        subject = request.form["subject"].upper()
        topic = request.form["topic"].upper()
        id = "".join(random.sample(string.hexdigits,6))
        date = datetime.now().date().strftime(r"%d/%m/%Y")
        filetype = file.filename.split(".")[-1]
        filename = secure_filename(subject+"_"+topic+"."+filetype)
        filelink = f"static/database/{filename}"
        file.save(filelink)
        if filetype == "doc" or filetype == "docx":
            convert(f"static/database/{filename}",f"static/database/{filename.split('.')[0] + '.pdf'}")
            Path(f"static/database/{filename}").unlink()
            filename = filename.split(".")[0] + ".pdf"
            filelink = f"static/database/{filename}"
            query = "insert into notes (id,date,filename,subjectname,filetype,filelink) values (%s,%s,%s,%s,%s,%s)"
            mycursor.executemany(query,[(id,date,filename,subject,"pdf",filelink)])
        else:
            query = "insert into notes (id,date,filename,subjectname,filetype,filelink) values (%s,%s,%s,%s,%s,%s)"
            mycursor.executemany(query,[(id,date,filename,subject,filetype,filelink)])
        mydb.commit()
        mycursor.close()
    return render_template("upload.html")

@app.route("/favorites",methods=["POST","GET"])
def favorites():
    choosefile = request.form.get("pdfbutton")
    if choosefile:
        choosefile = choosefile.replace("\'","\"")
        choosefile = json.loads(choosefile)
        return send_file(choosefile["filelink"],download_name=choosefile["filename"],as_attachment=True)
    unfavorite = request.form.get("unfavorite")
    if unfavorite:
        unfavorite = unfavorite.replace("\'","\"")
        unfavorite = json.loads(unfavorite)
        favoritelist.remove(unfavorite)
        print(favoritelist)
    return render_template("favorites.html",favoritelist=favoritelist)

@app.route("/addsubjects",methods=["POST","GET"])
def addsubject():
    mydb = mysql.connector.connect(host="localhost",user="root",password="",database="notesportal")
    mycursor = mydb.cursor()
    num=0
    tempnavsub = eval(navsub[5])
    username = navsub[3]
    query = "UPDATE `users` SET `subjects`=%s WHERE `username`=%s"
    if request.method == "POST":
        num = int(request.form["numsub"]) 
        try:
            for x in range(num):
                subject = request.form[f"subject_{x}"].upper()
                print(subject)
                if subject != "" and subject != " " and len(subject)!=0 and subject not in tempnavsub:
                    tempnavsub.append(subject)
            mycursor.execute(query,(str(tempnavsub),username))
            mydb.commit() 
        except KeyError:
            pass
    return render_template("addsubject.html",tempnavsub=tempnavsub,num=num)

@app.route("/removesubjects",methods=["POST","GET"])
def removesubject():
    mydb = mysql.connector.connect(host="localhost",user="root",password="",database="notesportal")
    mycursor = mydb.cursor()
    num=0
    tempnavsub = eval(navsub[5])
    username = navsub[3]
    query = "UPDATE `users` SET `subjects`=%s WHERE `username`=%s"
    if request.method == "POST":
        editsub = request.form.get("editsubject")
        print(editsub)
        try:
            print("code at remove")
            tempnavsub.remove(editsub)
            mycursor.execute(query,(str(tempnavsub),username))
            print("remove "+str(tempnavsub))
            navsub[5] = tempnavsub
            mydb.commit()
        except ValueError:
            pass
    return render_template("removesubjects.html",tempnavsub=tempnavsub,num=num)

@app.route("/signin",methods=["POST","GET"])
def signin():
    global navsub
    mydb = mysql.connector.connect(host="localhost",user="root",password="",database="notesportal")
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM users")
    userslst = mycursor.fetchall()
    if request.method == "POST":
        username = request.form["username"]
        for user in userslst:
                if user[3] == username:
                    navsub = user
                    print(user)
                    return redirect("/home")
    return render_template("signin.html")

if "__main__" == __name__:
    app.run(debug=True)