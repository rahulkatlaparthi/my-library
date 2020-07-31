import sqlite3 as sql


def insertUser(idcard_number, email, password):
    con = sql.connect("mylibrary.sqlite")
    cur = con.cursor()
    cur.execute("INSERT INTO user (idcard_number,email,password) VALUES (?,?,?)", (idcard_number, email, password))
    con.commit()
    con.close()


def retrieveUsers():
    con = sql.connect("mylibrary.sqlite")
    cur = con.cursor()
    cur.execute("SELECT idcard_number,email, password FROM user")
    user = cur.fetchall()
    con.close()
    return user
