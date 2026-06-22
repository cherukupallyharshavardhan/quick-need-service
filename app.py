# OTP Login System for Quick Need Service App
# Save as app.py

from flask import Flask, render_template_string, request, redirect, session
import random

app = Flask(__name__)
app.secret_key = "quickneed_otp_secret"


# -----------------------------------
# STEP 1 : MOBILE NUMBER PAGE
# -----------------------------------

mobile_page = """
<!DOCTYPE html>
<html>
<head>
<title>Quick Need Service - OTP Login</title>

<style>
body{
    margin:0;
    font-family:Arial;
    background:linear-gradient(120deg,#0f2027,#203a43,#2c5364);
    height:100vh;
    display:flex;
    justify-content:center;
    align-items:center;
}

.login-box{
    background:white;
    width:380px;
    padding:40px;
    border-radius:15px;
    box-shadow:0 15px 35px rgba(0,0,0,0.2);
    text-align:center;
}

h2{
    margin-bottom:25px;
    color:#2c3e50;
}

input{
    width:100%;
    padding:14px;
    margin:12px 0;
    border:1px solid #ddd;
    border-radius:8px;
    font-size:15px;
}

button{
    width:100%;
    padding:14px;
    background:#3498db;
    border:none;
    color:white;
    font-size:16px;
    border-radius:8px;
    cursor:pointer;
}

button:hover{
    background:#2980b9;
}
</style>

</head>
<body>

<div class="login-box">

<h2>Quick Need Service</h2>
<h3>Login with OTP</h3>

<form method="POST">
    <input
        type="text"
        name="mobile"
        placeholder="Enter Mobile Number"
        required
    >

    <button type="submit">
        Send OTP
    </button>
</form>

</div>

</body>
</html>
"""


# -----------------------------------
# STEP 2 : OTP VERIFY PAGE
# -----------------------------------

otp_page = """
<!DOCTYPE html>
<html>
<head>
<title>Verify OTP</title>

<style>
body{
    margin:0;
    font-family:Arial;
    background:#f4f6f9;
    height:100vh;
    display:flex;
    justify-content:center;
    align-items:center;
}

.box{
    background:white;
    width:380px;
    padding:40px;
    border-radius:15px;
    box-shadow:0 10px 25px rgba(0,0,0,0.1);
    text-align:center;
}

input{
    width:100%;
    padding:14px;
    margin:15px 0;
    border:1px solid #ccc;
    border-radius:8px;
}

button{
    width:100%;
    padding:14px;
    background:#27ae60;
    color:white;
    border:none;
    border-radius:8px;
    font-size:16px;
}
</style>

</head>
<body>

<div class="box">

<h2>Verify OTP</h2>

<p>OTP sent to {{ mobile }}</p>

<form method="POST">
    <input
        type="text"
        name="otp"
        placeholder="Enter OTP"
        required
    >

    <button type="submit">
        Verify OTP
    </button>
</form>

</div>

</body>
</html>
"""


# -----------------------------------
# STEP 3 : HOME PAGE
# -----------------------------------

home_page = """
<!DOCTYPE html>
<html>
<head>
<title>Quick Need Services</title>

<style>
body{
    font-family:Arial;
    background:#f4f6f9;
    margin:0;
}

.navbar{
    background:#2c3e50;
    color:white;
    padding:18px;
    display:flex;
    justify-content:space-between;
}

.services{
    display:grid;
    grid-template-columns:repeat(3,1fr);
    gap:25px;
    padding:40px;
}

.card{
    background:white;
    padding:30px;
    text-align:center;
    border-radius:12px;
    box-shadow:0 5px 15px rgba(0,0,0,0.08);
}

.btn{
    margin-top:15px;
    display:inline-block;
    padding:12px 20px;
    background:#3498db;
    color:white;
    text-decoration:none;
    border-radius:8px;
}
</style>

</head>
<body>

<div class="navbar">
    <h2>Quick Need Services</h2>

    <div>
        Welcome {{ mobile }}
        <a href="/logout" style="color:white;margin-left:20px;">
            Logout
        </a>
    </div>
</div>

<div class="services">

    <div class="card">
        <h3>Electrician</h3>
        <p>Fan, wiring, switch repairs</p>
        <a href="#" class="btn">Book Now</a>
    </div>

    <div class="card">
        <h3>Plumber</h3>
        <p>Pipe leakage & water problems</p>
        <a href="#" class="btn">Book Now</a>
    </div>

    <div class="card">
        <h3>AC Repair</h3>
        <p>AC service & gas refill</p>
        <a href="#" class="btn">Book Now</a>
    </div>

</div>

</body>
</html>
"""


# -----------------------------------
# ROUTE 1 : MOBILE NUMBER LOGIN
# -----------------------------------

@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        mobile = request.form["mobile"]

        # Generate 6-digit OTP
        otp = random.randint(100000, 999999)

        # Save in session
        session["mobile"] = mobile
        session["otp"] = str(otp)

        # Demo OTP shown in terminal
        print("================================")
        print("OTP for", mobile, "is:", otp)
        print("================================")

        return redirect("/verify-otp")

    return render_template_string(mobile_page)


# -----------------------------------
# ROUTE 2 : VERIFY OTP
# -----------------------------------

@app.route("/verify-otp", methods=["GET", "POST"])
def verify():

    if "mobile" not in session:
        return redirect("/")

    if request.method == "POST":
        entered_otp = request.form["otp"]

        if entered_otp == session["otp"]:
            session["logged_in"] = True
            return redirect("/home")

    return render_template_string(
        otp_page,
        mobile=session["mobile"]
    )


# -----------------------------------
# ROUTE 3 : HOME
# -----------------------------------

@app.route("/home")
def home():

    if "logged_in" not in session:
        return redirect("/")

    return render_template_string(
        home_page,
        mobile=session["mobile"]
    )


# -----------------------------------
# ROUTE 4 : LOGOUT
# -----------------------------------

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# -----------------------------------
# RUN APP
# -----------------------------------

import os

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )