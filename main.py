import os
import sqlite3
import time

from flask import Flask, render_template, url_for, request
from werkzeug.utils import redirect

app = Flask(__name__)

app.config['SECRET_KEY'] = 'keychik'
myd = dict()
result = ""
messages = ""
friend_id = ""
chat_id = ""


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/form.html', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template("form.html")
    else:
        global result
        myd = request.form.to_dict()
        con = sqlite3.connect("DeM.db")
        cur = con.cursor()
        result = cur.execute("""SELECT username, password FROM users
                WHERE username == ? AND password == ?""", (list(myd.values())[0],
                                                           list(myd.values())[1])).fetchone()

        if result:
            param = dict()
            param["back_url"] = url_for("static", filename="sea.jpg")
            param["username"] = list(myd.values())[0]
            return render_template("DeM.html", **param)
        else:
            return render_template("form.html")


@app.route('/DeM.html')
def DeM():
    param = dict()
    param["back_url"] = url_for("static", filename="sea.jpg")
    param["username"] = result[0]
    return render_template("DeM.html", **param)


@app.route('/register.html', methods=['POST', 'GET'])
def register():
    if request.method == 'GET':
        return render_template("register.html")
    else:
        if all(request.form.to_dict().values()):
            global myd
            myd = request.form.to_dict()
            con = sqlite3.connect("DeM.db")
            cur = con.cursor()
            cur.execute(f"""INSERT INTO users(username, password)
                    VALUES (?, ?)""", (list(myd.values())[0], list(myd.values())[1]))

            con.commit()
            return redirect("/DeM.html", code=302)


@app.route('/chats.html', methods=['POST', 'GET'])
def chats():
    if request.method == "GET":
        global myd
        param = dict()
        param["back_url"] = url_for("static", filename="sea.jpg")
        param["username"] = result[0]
        param["script_src"] = url_for("static", filename="choose.js")
        con = sqlite3.connect("DeM.db")
        cur = con.cursor()
        friends = cur.execute("""SELECT first, second FROM friends
                WHERE first == ? OR second == ?""", (result[0],
                                                     result[0])).fetchall()

        friends = list(map(lambda x: x[0] if x[0] != result[0] else x[1], friends))

        print(friends)

        param["friends"] = friends
        friend_id = cur.execute("""SELECT id FROM friends
                WHERE first == ? OR second == ?""", (result[0],
                                                     result[0])).fetchall()
        friend_id = list(map(lambda x: x[0], friend_id))
        len_friends = len(friend_id)
        friends_list = []
        for i in range(len(friend_id)):
            friends_list.append([friend_id[i], friends[i]])

        print(friend_id)
        param["friend_id"] = friend_id
        param["len_friends"] = len_friends
        param["messages"] = "\n\n".join(list(map(lambda x: f"{x[0]}: {x[1]}", messages)))
        return render_template("chats.html", **param)
    else:
        myd = request.form.to_dict()
        con = sqlite3.connect("DeM.db")
        cur = con.cursor()
        friend_id = cur.execute("""SELECT first, second FROM friends
                WHERE id == ?""", (chat_id,)).fetchone()
        print(friend_id)
        for i in friend_id:
            if i != result[0]:
                friend_id = i
                break
        cur.execute(f"""INSERT INTO messages(chat_id, sender, receiver, text)
                VALUES (?, ?, ?, ?)""", (chat_id, result[0], friend_id, request.form.to_dict()["text"]))

        con.commit()
        return choose_friend(chat_id)


@app.route('/choose_friend/<int:id>', methods=['GET', 'POST'])
def choose_friend(id):
    global messages, chat_id
    chat_id = id
    con = sqlite3.connect("DeM.db")
    cur = con.cursor()
    messages = cur.execute(f"""SELECT sender, text FROM messages
            WHERE (sender == '{result[0]}' or receiver == '{result[0]}') AND
                chat_id == {id}""").fetchall()

    return redirect("/chats.html", code=302)


@app.route('/friends.html', methods=['GET', 'POST'])
def action_with_friends():
    if request.method == "GET":
        param = dict()
        param["back_url"] = url_for("static", filename="sea.jpg")
        return render_template("friends.html", **param)
    else:
        myd = request.form.to_dict()
        con = sqlite3.connect("DeM.db")
        cur = con.cursor()
        res = cur.execute("""SELECT username FROM users
            WHERE username == ?""", (myd["name"],))

        print(res)

        if res:
            cur.execute("""INSERT INTO friends(first, second)
                VALUES (?, ?)""", (result[0], myd["name"]))

            con.commit()

        return redirect("/DeM.html", code=302)


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
