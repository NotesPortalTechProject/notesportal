from flask import Flask,render_template,redirect,send_file,request
import random,string,json
from datetime import datetime
from werkzeug.utils import secure_filename
from docx2pdf import convert
from pathlib import Path
from mailsend import sendmail
from supabase import create_client

app  = Flask(__name__)
favoritelist = []
data = ""
navsub = {}
supabase = create_client("https://pgyqwtttvyezvyyexbfh.supabase.co","eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBneXF3dHR0dnllenZ5eWV4YmZoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MDk2MjM0ODIsImV4cCI6MjAyNTE5OTQ4Mn0.Zeajgmmbh8Y2RoeUj4xTi25zQrVlIqGlr7fahbToKak")

@app.route("/",methods=["GET","POST"])
def index():
    id = "".join(random.sample(string.hexdigits,6))
    firstname = ""
    lastname = ""
    username = ""
    mail = ""
    num = 0
    subjectlst = []
    if request.method == "POST":
        firstname = request.form["firstname"]
        lastname = request.form["lastname"]
        username = request.form["username"]
        mail = request.form["email"]
        num = int(request.form["numsub"])
        userslst = supabase.table('users').select("*").eq('username',username).execute().data 
        if len(userslst) == 0:
            try:
                for x in range(num):
                    subjectlst.append(request.form[f"subject_{x}"].upper())
                sendmail(username,mail=mail)
                supabase.table('users').insert({"id": id,"firstname": firstname,"lastname": lastname,"username": username,"email": mail,"subjects": str(subjectlst)}).execute()
                navtemplst = [id,firstname,lastname,username,mail,str(subjectlst)]
                keylst = ["id","firstname","lastname","username","email","subjects"]
                for x in range(6):
                    navsub[keylst[x]] = navtemplst[x]
                return redirect("/home")
            except KeyError:
                pass
        else:
            print("User Already Exists")
            return redirect("/signin")
    return render_template("index.html",num=num,firstname=firstname,lastname=lastname,username=username,mail=mail)

@app.route("/home",methods=["POST","GET"])
def home():
    global navsub
    global data
    datalist = []
    # userslst = supabase.table('users').select("*").eq('subjectname',data).execute().data 
    # username = navsub["username"]
    # if not navsub:
    #     navsub = supabase.table('users').select("*").eq('username',username).execute().data 
        # for user in userslst:
        #     if user["username"] == username:
        #             navsub = user
        #             print(navsub)
        # print(navsub)
    if request.method == "POST":
        try:
            data = request.form["navbarsubject"]
        except KeyError:
            pass
        datalist = supabase.table('notes').select('*').eq('subjectname',data).execute().data
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
    return render_template("home.html",navsublst=eval(navsub["subjects"]),pdflist=datalist,favoritelist=favoritelist)

@app.route("/upload",methods=["POST","GET"])
def upload():
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
            supabase.table('notes').insert({"id": id,"date": date,"filename": filename,"subjectname": subject,"filetype": filetype,"filelink": filelink}).execute()
        else:
            supabase.table('notes').insert({"id": id,"date": date,"filename": filename,"subjectname": subject,"filetype": filetype,"filelink": filelink}).execute()
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
    return render_template("favorites.html",favoritelist=favoritelist)

@app.route("/addsubjects",methods=["POST","GET"])
def addsubject():
    num=0
    tempnavsub = eval(navsub["subjects"])
    username = navsub["username"]
    if request.method == "POST":
        num = int(request.form["numsub"]) 
        try:
            for x in range(num):
                subject = request.form[f"subject_{x}"].upper()
                print(subject)
                if subject != "" and subject != " " and len(subject)!=0 and subject not in tempnavsub:
                    tempnavsub.append(subject)
            supabase.table('users').update({'subjects':tempnavsub}).eq('username',username).execute()
        except KeyError:
            pass
    return render_template("addsubject.html",tempnavsub=tempnavsub,num=num)

@app.route("/removesubjects",methods=["POST","GET"])
def removesubject():
    num=0
    tempnavsub = eval(navsub["subjects"])
    username = navsub["username"]
    if request.method == "POST":
        editsub = request.form.get("editsubject")
        try:
            tempnavsub.remove(editsub)
            supabase.table('users').update({'subjects':tempnavsub}).eq('username',username).execute()
            navsub["subjects"] = str(tempnavsub)
            print(tempnavsub)
        except ValueError:
            pass
    return render_template("removesubjects.html",tempnavsub=tempnavsub,num=num)

@app.route("/signin",methods=["POST","GET"])
def signin():
    global navsub
    if request.method == "POST":
        username = request.form["username"]
        tempdict = supabase.table('users').select("*").eq('username',username).execute().data[0]
        for i,j in list(tempdict.items()):
            navsub[i] = j
        return redirect("/home")
    return render_template("signin.html")

if "__main__" == __name__:
    app.run(debug=True)