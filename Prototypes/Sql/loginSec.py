from tkinter import *
import mysql.connector
import time
import re
#connecting to the database
db = mysql.connector.connect(host="localhost",user="root",passwd="root",database="dblogin")
mycur = db.cursor()

# maximum number of login attempts allowed
MAX_LOGIN_ATTEMPTS = 3

# dictionary to store login attempts for each user
login_attempts = {}

def error_destroy():
    err.destroy()

def succ_destroy():
    succ.destroy()
    root1.destroy()

def error():
    global err
    err = Toplevel(root1)
    err.title("Error")
    err.geometry("200x100")
    Label(err,text="All fields are required..",fg="red",font="bold").pack()
    Label(err,text="").pack()
    Button(err,text="Ok",bg="grey",width=8,height=1,command=error_destroy).pack()

def success():
    global succ
    succ = Toplevel(root1)
    succ.title("Success")
    succ.geometry("200x100")
    Label(succ, text="Registration successful...", fg="green", font="bold").pack()
    Label(succ, text="").pack()
    Button(succ, text="Ok", bg="grey", width=8, height=1, command=succ_destroy).pack()

def register_user():
    username_info = username.get()
    password_info = password.get()
    if username_info == "":
        error()
    elif password_info == "":
        error()
    elif is_strong_password(str(password_info))==False:
        passwordValid()
    else:
        sql = "insert into dblogin values(%s,%s)"
        t = (username_info, password_info)
        mycur.execute(sql, t)
        db.commit()
        Label(root1, text="").pack()
        time.sleep(0.50)
        success()



def registration():
    global root1
    root1 = Toplevel(root)
    root1.title("Registration")
    root1.geometry("300x250")
    global username
    global password
    Label(root1,text="Register your account",bg="grey",fg="black",font="bold",width=300).pack()
    username = StringVar()
    password = StringVar()
    Label(root1,text="").pack()
    Label(root1,text="Username :",font="bold").pack()
    Entry(root1,textvariable=username).pack()
    Label(root1, text="").pack()
    Label(root1, text="Password :").pack()
    Entry(root1, textvariable=password,show="*").pack()
    Label(root1, text="").pack()
    Button(root1,text="Register",bg="red",command=register_user).pack()

def login():
    global root2
    root2 = Toplevel(root)
    root2.title("Login")
    root2.geometry("300x300")
    global username_varify
    global password_varify
    Label(root2, text="Login", bg="grey", fg="black", font="bold",width=300).pack()
    username_varify = StringVar()
    password_varify = StringVar()
    Label(root2, text="").pack()
    Label(root2, text="Username :", font="bold").pack()
    Entry(root2, textvariable=username_varify).pack()
    Label(root2, text="").pack()
    Label(root2, text="Password :").pack()
    Entry(root2, textvariable=password_varify, show="*").pack()
    Label(root2, text="").pack()
    Button(root2, text="Login", bg="red",command=login_varify).pack()
    Label(root2, text="")

def logg_destroy():
    logg.destroy()
    root2.destroy()

def fail_destroy():
    fail.destroy()

def logged():
    global logg
    logg = Toplevel(root2)
    logg.title("Welcome")
    logg.geometry("200x100")
    Label(logg, text="Welcome {} ".format(username_varify.get()), fg="green", font="bold").pack()
    Label(logg, text="").pack()
    Button(logg, text="Log-Out", bg="grey", width=8, height=1, command=logg_destroy).pack()


def failed():
    global fail
    fail = Toplevel(root2)
    fail.title("Invalid")
    fail.geometry("200x100")
    Label(fail, text="Invalid credentials...", fg="red", font="bold").pack()
    Label(fail, text="").pack()
    Button(fail, text="Ok", bg="grey", width=8, height=1, command=fail_destroy).pack()
def is_strong_password(password):
    """Checks if the given password is strong.

    A strong password must meet the following criteria:
    - Be at least 8 characters long
    - Contain at least one lowercase letter
    - Contain at least one uppercase letter
    - Contain at least one digit
    - Contain at least one special character: !@#$%^&*()-_=+[]{};:'",.<>/?\|

    Args:
        password (str): The password to check.

    Returns:
        bool: True if the password is strong, False otherwise.
    """
    import re
    pattern = re.compile(
        r'^(?=.[a-z])(?=.[A-Z])(?=.\d)(?=.[!@#$%^&()-_=+[\]{};:\'",.<>/?\\|])[A-Za-z\d!@#$%^&()-_=+[\]{};:\'",.<>/?\\|]{8,}$'
    )
    return bool(pattern.match(password))

def toMany():
    global fail
    fail = Toplevel(root2)
    fail.title("Invalid")
    fail.geometry("300x100")
    Label(fail, text="user is blocked, to many fails...", fg="red", font="bold").pack()
    Label(fail, text="").pack()
    Button(fail, text="Ok", bg="grey", width=8, height=1, command=fail_destroy).pack()
def passwordValid():
    global fail
    fail = Toplevel(root1)
    fail.title("Invalid")
    fail.geometry("500x100")
    Label(fail, text="Password must be least 8 characters long\nContain at least one lowercase letter\nContain at least one uppercase letter\nContain at least one digit\Contain at least one special character", fg="red", font="bold").pack()
    Label(fail, text="").pack()
    Button(fail, text="Ok", bg="grey", width=8, height=1, command=fail_destroy).pack()
def login_varify():
    user_varify = username_varify.get()
    pas_varify = password_varify.get()
    sql = "select * from dblogin where user = %s and password = %s"
    mycur.execute(sql,[(user_varify),(pas_varify)])
    results = mycur.fetchall()
    if(user_varify in login_attempts and login_attempts[user_varify]>2):
        toMany()
        return
    if results:
        for i in results:
            logged()
            break
    else:
        if user_varify in login_attempts:
            login_attempts[user_varify] += 1
        else:
            login_attempts[user_varify]=1


        failed()


def main_screen():
    global root
    root = Tk()
    root.title("Login")
    root.geometry("300x300")
    Label(root,text="login",font="bold",bg="grey",fg="black",width=300).pack()
    Label(root,text="").pack()
    Button(root,text="Login",width="8",height="1",bg="red",font="bold",command=login).pack()
    Label(root,text="").pack()
    Button(root, text="Registration",height="1",width="15",bg="red",font="bold",command=registration).pack()
    Label(root,text="").pack()
    Label(root,text="").pack()


main_screen()
root.mainloop()