from flask import Flask, render_template, request, url_for, redirect
import sqlite3

app = Flask(__name__)
connection = sqlite3.connect("main.db")
cursor = connection.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS pages (name TEXT, code TEXT)")
connection.commit()

# build the raw HTML code of the demo page and save it as a text file (demo.html)
# the goal is to make the raw HTML code of the demo page accessible to the user
with (open("templates/demo.txt", "w")) as f:
    f.write(open("templates/demo.html").read().replace("<", "&lt;")
            .replace(">", "&gt;").replace("\n", "<br>")
            .replace(" ", "&nbsp;"))

# same with css
with (open("static/demo_style.txt", "w")) as f:
    f.write(open("static/demo_style.css").read().replace("<", "&lt;")
            .replace(">", "&gt;").replace("\n", "<br>")
            .replace(" ", "&nbsp;"))

@app.route("/")
def main():
    con = sqlite3.connect("main.db")
    cur = con.cursor()
    page_list = cur.execute("SELECT name, rowid FROM pages").fetchall()
    return render_template("index.html", pages=page_list)

@app.route("/demo")
@app.route("/demo/")
def demo():
    return render_template("demo.html")

@app.route("/demo/html")
@app.route("/demo/html/")
def html():
    return open("templates/demo.txt").read()

@app.route("/demo/css")
@app.route("/demo/css/")
def css():
    return open("static/demo_style.txt").read()

@app.route("/submit", methods=["GET", "POST"])
def submit():
    message = ""
    if request.method == "POST":
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

@app.route("/raw/<int:id>")
def raw(id):
    con = sqlite3.connect("main.db")
    cur = con.cursor()
    code = cur.execute("SELECT code FROM pages WHERE rowid=?", (id,)).fetchone()
    return f"<pre>{code[0]}</pre>"
