from flask import Flask, render_template, request, redirect, session
from db import get_db
from blockchain import blockchain
import bcrypt
import hashlib

app = Flask(__name__)
app.secret_key = "secret123"


# 🔐 LOGIN
@app.route("/", methods=["GET","POST"])
def login():
    error = None

    if request.method == "POST":
        voter = request.form["voter"]
        password = request.form["password"]

        db = get_db()
        cur = db.cursor(dictionary=True)

        cur.execute("SELECT * FROM voters WHERE voter_id=%s",(voter,))
        user = cur.fetchone()

        if user:

            # 🔴 Account lock check
            if user["attempts"] >= 3:
                return "Account locked due to multiple failed attempts!"

            # 🔐 Password verification
            if bcrypt.checkpw(password.encode(), user["password"].encode()):

                # reset attempts
                cur.execute("UPDATE voters SET attempts=0 WHERE voter_id=%s",(voter,))

                # log login
                cur.execute("INSERT INTO logs (voter_id,action) VALUES (%s,%s)",(voter,"login"))

                session["voter"] = voter
                db.commit()

                return redirect("/vote")

            else:
                # increase attempts
                cur.execute("UPDATE voters SET attempts=attempts+1 WHERE voter_id=%s",(voter,))
                db.commit()
                error = "Wrong password"

        else:
            error = "Invalid user"

    return render_template("login.html", error=error)


# 🗳️ VOTING
@app.route("/vote", methods=["GET","POST"])
def vote():

    if "voter" not in session:
        return redirect("/")

    db = get_db()
    cur = db.cursor(dictionary=True)

    cur.execute("SELECT * FROM voters WHERE voter_id=%s",(session["voter"],))
    user = cur.fetchone()

    # 🔴 prevent double voting
    if user["has_voted"] == 1:
        return "You already voted!"

    if request.method == "POST":
        candidate = request.form["candidate"]

        # 🔐 hash vote
        vote_hash = hashlib.sha256(candidate.encode()).hexdigest()

        # ⛓️ add to blockchain
        blockchain.add_block(vote_hash)

        # update voter
        cur.execute("UPDATE voters SET has_voted=1 WHERE voter_id=%s",(session["voter"],))

        # log vote
        cur.execute("INSERT INTO logs (voter_id,action) VALUES (%s,%s)",(session["voter"],"vote"))

        db.commit()

        return redirect("/result")

    return render_template("vote.html")


# 📊 RESULT + BLOCKCHAIN CHECK
@app.route("/result")
def result():
    valid = blockchain.is_valid()
    return render_template("result.html", chain=blockchain.chain, valid=valid)


# 🛠️ ADMIN LOG VIEW
@app.route("/admin")
def admin():
    db = get_db()
    cur = db.cursor(dictionary=True)

    cur.execute("SELECT * FROM logs")
    logs = cur.fetchall()

    return render_template("admin.html", logs=logs)


app.run(debug=True)