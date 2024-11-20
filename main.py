from flask import Flask, render_template, request, url_for, redirect
import sqlite3

app = Flask(__name__)

@app.route("/")
def main():
    con = sqlite3.connect("main.db")
    cur = con.cursor()
    page_list = cur.execute("SELECT name, rowid FROM pages").fetchall()
    return render_template("index.html", pages=page_list)

@app.route("/submit", methods=["GET", "POST"])
def submit():
    message = ""
    if (request.method == "POST"):
        if request.form["name"] == "":
            message = "name field is empty"
        else:
            name = request.form["name"]
            code = request.form["code"]
            print(code)

            submit_file(name, code)
            print(code)

            return redirect(url_for("main"))
    return render_template("submit.html", message=message)

def submit_file(name, code):
    con = sqlite3.connect("main.db")
    cur = con.cursor()
    print(f"Submitting {name}'s code: {code}")
    cur.execute("INSERT INTO pages VALUES(?, ?)", (name, code))
    con.commit()

@app.route("/page/<int:id>")
def page(id):
    con = sqlite3.connect("main.db")
    cur = con.cursor()
    code = cur.execute("SELECT code FROM pages WHERE rowid=?", (id,)).fetchone()
    return code[0]