from flask import Flask, request, redirect, url_for, render_template_string, session
import db
from config import ADMIN_PASSWORD

app=Flask(__name__)
app.secret_key="CHANGE_THIS_SECRET_KEY"

LOGIN="""
<h2>Office Admin Login</h2>
<form method="post">
<input name="password" type="password" placeholder="Password">
<button>Login</button>
</form>
"""

PAGE="""
<!doctype html><html><head><meta charset="utf-8">
<title>Office Admin</title>
<style>
body{font-family:Arial;margin:25px;background:#f5f5f5}
.card{background:white;padding:20px;margin-bottom:20px;border-radius:10px}
table{border-collapse:collapse;width:100%;background:white}
th,td{padding:9px;border-bottom:1px solid #ddd;text-align:left}
.late{color:#b00020;font-weight:bold}.ok{color:green;font-weight:bold}
</style></head><body>
<h1>Office Admin Panel</h1>
<div class="card"><h3>Break Limits</h3>
<form method="post" action="/limits">
{% for k,v in limits.items() %}
<label>{{k}} <input name="{{k}}" type="number" min="1" value="{{v}}"> min</label>
{% endfor %}<button>Save</button></form></div>

<div class="card"><h3>Employees</h3><table>
<tr><th>Name</th><th>Username</th><th>Telegram ID</th><th>Status</th></tr>
{% for e in employees %}
<tr><td>{{e['name']}}</td><td>{{e['username']}}</td><td>{{e['telegram_id']}}</td>
<td>{{'Active' if e['active'] else 'Inactive'}}</td></tr>
{% endfor %}</table></div>

<div class="card"><h3>Recent Punch History</h3><table>
<tr><th>Employee</th><th>Activity</th><th>Start</th><th>Return</th><th>Duration</th><th>Status</th></tr>
{% for e in events %}
<tr><td>{{e['name']}}</td><td>{{e['event_type']}}</td>
<td>{{e['started_at']}}</td><td>{{e['ended_at'] or 'Still active'}}</td>
<td>{% if e['ended_at'] and e['limit_minutes'] %}{{e['limit_minutes'] + e['late_minutes']}}
{% elif e['ended_at'] %}—{% else %}—{% endif %}</td>
<td>{% if e['late_minutes'] %}<span class="late">Late {{e['late_minutes']}} min</span>
{% elif e['ended_at'] and e['event_type'] in ['eat','smoke','toilet'] %}
<span class="ok">On time</span>
{% elif e['event_type']=='work' %}Working{% else %}Active{% endif %}</td></tr>
{% endfor %}</table></div>
</body></html>
"""

def logged_in(): return session.get("admin") is True

@app.route("/",methods=["GET","POST"])
def login():
    if request.method=="POST":
        if request.form.get("password")==ADMIN_PASSWORD:
            session["admin"]=True
            return redirect(url_for("dashboard"))
        return "Wrong password",401
    return redirect(url_for("dashboard")) if logged_in() else render_template_string(LOGIN)

@app.get("/dashboard")
def dashboard():
    if not logged_in(): return redirect(url_for("login"))
    return render_template_string(PAGE,limits=db.get_limits(),
                                  employees=db.list_employees(),
                                  events=db.all_events())

@app.post("/limits")
def limits():
    if not logged_in(): return redirect(url_for("login"))
    for k in ("eat","smoke","toilet"):
        try: db.set_limit(k,max(1,int(request.form.get(k,"1"))))
        except ValueError: pass
    return redirect(url_for("dashboard"))

if __name__=="__main__":
    app.run(host="127.0.0.1",port=5000,debug=False)
