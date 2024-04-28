from flask import Flask,render_template,request
from flask_session import Session
from supabase import create_client,StorageException

app  = Flask(__name__)
app.secret_key = "please_work"
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
supabase = create_client("https://pgyqwtttvyezvyyexbfh.supabase.co","eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBneXF3dHR0dnllenZ5eWV4YmZoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MDk2MjM0ODIsImV4cCI6MjAyNTE5OTQ4Mn0.Zeajgmmbh8Y2RoeUj4xTi25zQrVlIqGlr7fahbToKak")


@app.route("/",methods=["GET","POST"])
def home():
    name = request.form.get("name")
    email = request.form.get("email")
    flag = 0
    if name and email:
        supabase.table("waitlist").insert({"name":name,"email":email}).execute()
        flag = 1
    return render_template("waitlist.html",flag=flag)

if "__main__" == __name__:
    app.run(debug=True)
