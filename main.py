from flask import Flask,render_template,redirect,send_file,request,url_for,session
from flask_session import Session
import random,string,json
from datetime import datetime
from werkzeug.utils import secure_filename
# from mailsend import sendmail
from supabase import create_client

app  = Flask(__name__)
app.secret_key = "please_work"
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
supabase = create_client("https://pgyqwtttvyezvyyexbfh.supabase.co","eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBneXF3dHR0dnllenZ5eWV4YmZoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MDk2MjM0ODIsImV4cCI6MjAyNTE5OTQ4Mn0.Zeajgmmbh8Y2RoeUj4xTi25zQrVlIqGlr7fahbToKak")

@app.route("/",methods=["GET","POST"])
def index():
    navsub = {}
    id = "".join(random.sample(string.hexdigits,6))
    firstname = ""
    lastname = ""
    username = ""
    mail = ""
    num = 0
    subjectlst = []
    session["data"] = ""
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
                #sendmail(username,mail=mail)
                supabase.table('users').insert({"id": id,"firstname": firstname,"lastname": lastname,"username": username,"email": mail,"subjects": str(subjectlst)}).execute()
                navtemplst = [id,firstname,lastname,username,mail,str(subjectlst)]
                keylst = ["id","firstname","lastname","username","email","subjects"]
                for x in range(6):
                    navsub[keylst[x]] = navtemplst[x]
                return redirect(url_for("home",id=id))
            except KeyError:
                pass
        else:
            print("User Already Exists")
            return redirect(url_for("/signin"))
    return render_template("index.html",num=num,firstname=firstname,lastname=lastname,username=username,mail=mail,id=id)

@app.route("/home/<id>",methods=["POST","GET"])
def home(id):
    navsub = supabase.table('users').select('*').eq('id',id).execute().data[0]
    favoritelist = supabase.table('users').select('favorites').eq('id',id).execute().data[0]["favorites"]
    datalist = []
    if not favoritelist:
        favoritelist = []
    data = session.get("data")
    if request.method == "POST":
        try:
            data = request.form.get("navbarsubject")
            if data != None:
                session["data"] = data
                datalist = supabase.table('notes').select('*').eq('subjectname',data).execute().data
        except KeyError:
            pass
        choosefile = request.form.get("pdfbutton")
        if choosefile:
            choosefile = choosefile.replace("\'","\"")
            choosefile = json.loads(choosefile)
            return send_file(choosefile["filelink"],download_name=choosefile["filename"],as_attachment=True)
        favorite = request.form.get("favorite")
        if favorite and favorite not in str(favoritelist):
            data = session.get("data")
            datalist = supabase.table('notes').select('*').eq('subjectname',data).execute().data
            favoritelist += " " + favorite
            supabase.table('users').update({'favorites':favoritelist}).eq('id',id).execute()
        elif favorite and (favorite in favoritelist):
            data = session.get("data")
            datalist = supabase.table('notes').select('*').eq('subjectname',data).execute().data
            favoritelist = favoritelist.replace(favorite,"")
            supabase.table('users').update({'favorites':favoritelist}).eq('id',id).execute()
    return render_template("home.html",navsublst=eval(navsub["subjects"]),pdflist=datalist,favoritelist=favoritelist,id=navsub["id"])

@app.route("/upload/<id>",methods=["POST","GET"])
def upload(id):
    if request.method == "POST":
        file = request.files["file"]
        subject = request.form["subject"].upper()
        topic = request.form["topic"].upper()
        idnote = "".join(random.sample(string.hexdigits,6))
        date = datetime.now().date().strftime(r"%d/%m/%Y")
        filetype = file.filename.split(".")[-1]
        filename = secure_filename(subject+"_"+topic+"."+filetype)
        filelink = f"static/database/{filename}"
        file.save(filelink)
        supabase.table('notes').insert({"id": idnote,"date": date,"filename": filename,"subjectname": subject,"filetype": filetype,"filelink": filelink}).execute()
    return render_template("upload.html",id=id)

@app.route("/favorites/<id>",methods=["POST","GET"])
def favorites(id):
    notesid = supabase.table('users').select('favorites').eq('id',id).execute().data[0]["favorites"]
    idlist = notesid.strip().split(" ")
    favoritelist = supabase.table("notes").select("*").in_("id",idlist).execute().data
    if request.method == "POST":
        choosefile = request.form.get("pdfbutton")
        if choosefile:
            choosefile = choosefile.replace("\'","\"")
            choosefile = json.loads(choosefile)
            return send_file(choosefile["filelink"],download_name=choosefile["filename"],as_attachment=True)
        unfavorite = request.form.get("unfavorite")
        if unfavorite:
            notesid = notesid.replace(unfavorite,"")
            supabase.table('users').update({'favorites':notesid}).eq('id',id).execute()
    return render_template("favorites.html",favoritelist=favoritelist,id=id)

@app.route("/addsubjects/<id>",methods=["POST","GET"])
def addsubject(id):
    navsub = supabase.table('users').select('*').eq('id',id).execute().data[0]
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
            navsub["subjects"] = str(tempnavsub)
            supabase.table('users').update({'subjects':tempnavsub}).eq('username',username).execute()
        except KeyError:
            pass
    return render_template("addsubject.html",tempnavsub=tempnavsub,num=num,id=id)

@app.route("/removesubjects/<id>",methods=["POST","GET"])
def removesubject(id):
    navsub = supabase.table('users').select('*').eq('id',id).execute().data[0]
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
    return render_template("removesubjects.html",tempnavsub=tempnavsub,num=num,id=id)

@app.route("/signin",methods=["POST","GET"])
def signin():
    navsub = {}
    session["data"] = ""
    if request.method == "POST":
        username = request.form["username"]
        tempdict = supabase.table('users').select("*").eq('username',username).execute().data[0]
        for i,j in list(tempdict.items()):
            navsub[i] = j
        return redirect(url_for("home",id=navsub["id"]))
    return render_template("signin.html")

if "__main__" == __name__:
    app.run(debug=True)
