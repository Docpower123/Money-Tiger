import mysql.connector

mydb = mysql.connector.connect(host="localhost", user="root", passwd="lian230106", database="info")

mycursor=mydb.cursor()
mycursor.execute("select*from signin")

for i in mycursor:
    print (i)