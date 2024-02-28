import mysql.connector
from datetime import datetime
from docx2pdf import convert
import random,string
from werkzeug.utils import secure_filename
from pathlib import Path

def uploadfile(file,subject):
    mydb = mysql.connector.connect(host="localhost",user="root",password="",database="notesportal")
    mycursor = mydb.cursor()
    id = "".join(random.sample(string.hexdigits,6))
    date = datetime.now().date().strftime(r"%d/%m/%Y")
    filetype = file.filename.split(".")[-1]
    filename = secure_filename(file.filename)
    filelink = f"static/database/{filename}"
    file.save(f"static/database/{filename}")
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


def downloadfile(data):
    datalist = []
    mydb = mysql.connector.connect(host="localhost",user="root",password="",database="notesportal")
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM notes")
    fetchdata = mycursor.fetchall()
    for element in fetchdata:
        if data in element[2]:
            eledict = {}
            eledict["id"] = element[0]
            eledict["date"] = element[1]
            eledict["filename"] = element[2]
            eledict["subjectname"] = element[3]
            eledict["filetype"] = element[4]
            eledict["filelink"] = element[5]
            print("found")
            datalist.append(eledict)
    return datalist
    
