from flask import Flask, render_template, request, url_for, redirect
import sqlite3

app = Flask(__name__)
connection = sqlite3.connect("main.db")
cursor = connection.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS pages (name TEXT, code TEXT)")
connection.commit()

def html_to_plaintext(html):
    return "<pre>"+html.replace("<", "&lt;").replace(">", "&gt;")+"</pre>"


# build the raw HTML code of the demo page and save it as a text file (demo.html)
# the goal is to make the raw HTML code of the demo page accessible to the user
with (open("templates/demo.txt", "w")) as f:
    f.write(html_to_plaintext(open("templates/demo.html").read()))

# same with css
with (open("static/demo_style.txt", "w")) as f:
    f.write(html_to_plaintext(open("static/demo_style.css").read()))

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

@app.route("/page/<int:num>")
def page(num):
    con = sqlite3.connect("main.db")
    cur = con.cursor()
    code = cur.execute("SELECT code FROM pages WHERE rowid=?", (num,)).fetchone()
    return code[0]

@app.route("/page/<int:num>/raw")
@app.route("/raw/<int:num>")
def raw(num):
    con = sqlite3.connect("main.db")
    cur = con.cursor()
    code = cur.execute("SELECT code FROM pages WHERE rowid=?", (num,)).fetchone()
    return html_to_plaintext(code[0])
