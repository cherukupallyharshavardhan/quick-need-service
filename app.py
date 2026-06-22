from flask import Flask, render_template_string, request, redirect, session
import os

app = Flask(**name**)
app.secret_key = "quickneed_secret"

# Temporary user storage

users = {}

# ----------------------------

# SIGN IN PAGE

# ----------------------------

signin_page = """

<!DOCTYPE html>

<html>
<head>
<title>Quick Need Service - Sign In</title>
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
.box{
    background:white;
    width:380px;
    padding:40px;
    border-radius:15px;
    text-align:center;
}
input{
    width:100%;
    padding:14px;
    margin:12px 0;
}
button{
    width:100%;
    padding:14px;
    background:#3498db;
    color:white;
    border:none;
}
a{
    text-decoration:none;
}
</style>
</head>
<body>

<div class="box">
<h2>Quick Need Service</h2>
<h3>Sign In</h3>

<form method="POST">
<input type="text" name="mobile" placeholder="Mobile Number" required>
<input type="password" name="password" placeholder="Password" required>

<button type="submit">Login</button>

</form>

<br>

<a href="/signup">Create New Account</a>

</div>

</body>
</html>
"""

# ----------------------------

# SIGN UP PAGE

# ----------------------------

signup_page = """

<!DOCTYPE html>

<html>
<head>
<title>Quick Need Service - Sign Up</title>
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
    text-align:center;
}
input{
    width:100%;
    padding:14px;
    margin:12px 0;
}
button{
    width:100%;
    padding:14px;
    background:#27ae60;
    color:white;
    border:none;
}
</style>
</head>
<body>

<div class="box">

<h2>Create Account</h2>

<form method="POST">

<input type="text" name="mobile" placeholder="Mobile Number" required>

<input type="password" name="password" placeholder="Password" required>

<button type="submit">
Create Account
</button>

</form>

<br>

<a href="/signin">Already have an account?</a>

</div>

</body>
</html>
"""

# ----------------------------

# HOME PAGE

# ----------------------------

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

<a href="/logout"
style="color:white;margin-left:20px;">
Logout </a>

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

# ----------------------------

# ROUTES

# ----------------------------

@app.route("/")
def root():
return redirect("/signin")

@app.route("/signup", methods=["GET", "POST"])
def signup():

```
if request.method == "POST":

    mobile = request.form["mobile"]
    password = request.form["password"]

    users[mobile] = password

    return redirect("/signin")

return render_template_string(signup_page)
```

@app.route("/signin", methods=["GET", "POST"])
def signin():

```
if request.method == "POST":

    mobile = request.form["mobile"]
    password = request.form["password"]

    if mobile in users and users[mobile] == password:

        session["logged_in"] = True
        session["mobile"] = mobile

        return redirect("/home")

    return "Invalid Login"

return render_template_string(signin_page)
```

@app.route("/home")
def home():

```
if "logged_in" not in session:
    return redirect("/signin")

return render_template_string(
    home_page,
    mobile=session["mobile"]
)
```

@app.route("/logout")
def logout():

```
session.clear()

return redirect("/signin")
```

# ----------------------------

# RUN APP

# ----------------------------

if **name** == "**main**":
app.run(
host="0.0.0.0",
port=int(os.environ.get("PORT", 5000))
)
