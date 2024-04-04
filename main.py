from flask import Flask,render_template,redirect,send_file,request,url_for,session,flash
from flask_session import Session
import random,string,json
from datetime import datetime
from werkzeug.utils import secure_filename
from mailsend import sendmail
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
    password = ""
    num = 0
    subjectlst = []
    mode=''
    if request.method == "POST":
        data=request.form
        if(data['flag']=='signup'):
            firstname = request.form["firstname"]
            lastname = request.form["lastname"]
            username = request.form["username"]
            password = request.form["password"]
            mail = request.form["email"]
            num = int(request.form["numsub"])
            userslst = supabase.table('users').select("*").eq('username',username).execute().data
            if(len(userslst)==0):
                try:
                    mode='sign-up-mode'
                    for x in range(num):
                        subjectlst.append(request.form[f"subject_{x}"].upper())
                    session["data"] = subjectlst[0]
                    sendmail(username,mail=mail,message=f"""Hello {username},
                             Welcome To Our Portal""")
                    supabase.table('users').insert({"id": id,"firstname": firstname,"lastname": lastname,"username": username,"email": mail,"subjects": str(subjectlst),"password":password}).execute()
                    navtemplst = [id,firstname,lastname,username,mail,str(subjectlst),password]
                    keylst = ["id","firstname","lastname","username","email","subjects","password"]
                    for x in range(6):
                        navsub[keylst[x]] = navtemplst[x]
                        return redirect(url_for("home",id=id))
                except KeyError:
                    pass
            else:
                mode=''
                errorflag=0
                userdata= supabase.table('users').select("*").eq('username',username).execute().data[0]
                if(userdata['username']==username):
                    errorflag=1
                elif(userdata['email']==mail):
                    errorflag=2
                return render_template('errors.html',F=errorflag)
        elif(data['flag']=='signin'):
                navsub = {}
                session["data"] = ""
                username = request.form["username"]
                password = request.form["password"]
                tempdict = supabase.table('users').select("*").eq('username',username).execute().data
                checkpass = supabase.table('users').select("password").eq('username',username).execute().data[0]["password"]
                if checkpass == password:
                    if(len(tempdict)==0):
                        errorflag=3
                        return render_template('errors.html',F=errorflag)
                    else:
                        tempdict=tempdict[0]
                        for i,j in list(tempdict.items()):
                            navsub[i] = j
                        sendmail(name=navsub["username"],mail=navsub["email"],message=f"""Hello {navsub["username"]},
                                Welcome Back To Our Portal""")
                        return redirect(url_for("home",id=navsub["id"]))
                else:
                    flash("Incorrect Password")
    return render_template("index.html",mode=mode,num=num,firstname=firstname,lastname=lastname,username=username,mail=mail,id=id,password=password)

@app.route("/home/<id>",methods=["POST","GET"])
def home(id):
    navsub = supabase.table('users').select('*').eq('id',id).execute().data[0]
    favoritelist = supabase.table('users').select('favorites').eq('id',id).execute().data[0]["favorites"]
    datalist = []
    preview = ""
    tempnavsub = eval(navsub["subjects"])
    active = ""
    active_r = ""
    active_u = ""
    num=0
    if not favoritelist:
        favoritelist = ""
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
        favorite = request.form.get("favorite")
        print(data)
        if choosefile:
            choosefile = choosefile.replace("\'","\"")
            choosefile = json.loads(choosefile)
            return send_file(choosefile["filelink"],download_name=choosefile["filename"],as_attachment=True)
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
        try:
            num = int(request.form["numsub"]) 
            username = navsub["username"]
            print(num)
            if num:
                active = "active"
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
        except KeyError:
            pass
        try:
            tempnavsub = eval(navsub["subjects"])
            username = navsub["username"]
            editsub = request.form.get("editsubject")
            if editsub:
                active_r = "active"
            else:
                active_r = ""
            try:
                tempnavsub.remove(editsub)
                supabase.table('users').update({'subjects':tempnavsub}).eq('username',username).execute()
                navsub["subjects"] = str(tempnavsub)
                print(tempnavsub)
            except ValueError:
                pass
        except KeyError:
            pass
        try:
            file = request.files["file"]
            subject = request.form["subject"].upper()
            topic = request.form["topic"].upper()
            idnote = "".join(random.sample(string.hexdigits,6))
            date = datetime.now().date().strftime(r"%d/%m/%Y")
            filetype = file.filename.split(".")[-1]
            filename = secure_filename(subject+"_"+topic+"."+filetype)
            filelink = f"static/database/{filename}"
            file.save(filelink)
            if filetype !="pdf":
                print("Please Upload Only PDFs")
                flash("Please Upload Only PDFs")
                active_u = "active"
            else:
                active_u = ""
                resp = supabase.storage.from_("userfilestorage").upload(filename,filelink,{"content-type":"application/pdf"})
                print(resp)
                fileurl = supabase.storage.from_("userfilestorage").get_public_url(filename)
                print(fileurl)
                supabase.table('notes').insert({"id": idnote,"date": date,"filename": filename,"subjectname": subject,"filetype": filetype,"filelink": fileurl}).execute()
        except KeyError:
            pass
    return render_template("home.html",active_u=active_u,active=active,navsublst=eval(navsub["subjects"]),pdflist=datalist,favoritelist=favoritelist,id=navsub["id"],data=data,username=navsub["username"],previewfile=preview,num=num,tempnavsub=tempnavsub,active_r=active_r)

@app.route("/favorites/<id>",methods=["POST","GET"])
def favorites(id):
    notesid = supabase.table('users').select('favorites').eq('id',id).execute().data[0]["favorites"]
    idlist = notesid.strip().split(" ")
    favoritelist = []
    favoritelist = supabase.table("notes").select("*").in_("id",idlist).execute().data
    if favoritelist:
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

@app.route("/sharvil")
def sharvil():
    return render_template("sharvil.html")

if "__main__" == __name__:
    app.run(debug=True)