import smtplib
from email.message import EmailMessage
mail_lst = ["naitechh@gmail.com"] # add list of celebrity emails 
# can import from file but need to write extra code
def sendmail(name,mail):
    msg = EmailMessage()
    s = smtplib.SMTP("smtp.gmail.com",587)
    s.starttls()
    s.login("pysendab@gmail.com","kueb sjyv hbhe xhlm")
    msg['Subject'] = "Welcome User"
    msg['From'] = "pysendab@gmail.com"
    msg['To'] = mail
    message = f"""Hello {name}
    Welcome To Our Portal"""
    msg.set_content(message)
    s.send_message(msg)
    s.quit()