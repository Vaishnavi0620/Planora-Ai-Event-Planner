
import os
import io
import sqlite3
from datetime import date
from flask import (
    Flask, request, render_template_string,
    redirect, url_for, session, send_file
)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret-before-deploy")
DB = os.environ.get("DATABASE_PATH", "planora.db")


def connect():
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    return db


def init_db():
    with connect() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS events (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            location TEXT NOT NULL,
            guests INTEGER NOT NULL,
            budget REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT NOT NULL,
            amount REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS guests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id TEXT NOT NULL,
            name TEXT NOT NULL,
            contact TEXT DEFAULT '',
            rsvp TEXT NOT NULL DEFAULT 'Pending'
        );
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id TEXT NOT NULL,
            title TEXT NOT NULL,
            due_date TEXT DEFAULT '',
            done INTEGER NOT NULL DEFAULT 0
        );
        """)


init_db()


def current_event():
    event_id = session.get("event_id")
    if not event_id:
        return None
    with connect() as db:
        return db.execute(
            "SELECT * FROM events WHERE id=?", (event_id,)
        ).fetchone()


HTML = """
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Planora | Event Manager</title>
<style>
*{box-sizing:border-box}
body{margin:0;background:#f7f5fc;color:#29223f;
font-family:Arial,sans-serif}
header{background:white;padding:22px 6%;display:flex;
justify-content:space-between;align-items:center;border-bottom:1px solid #eee}
.logo{font-size:25px;font-weight:bold;color:#7452e8}
main{max-width:1100px;margin:30px auto;padding:0 18px}
h1{font-size:32px}h2{font-size:21px}
p{line-height:1.5}
.muted{color:#77748b}
.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px}
.card{background:white;border:1px solid #ece8f5;border-radius:16px;
padding:22px;margin-bottom:18px;min-width:0}
input,select{width:100%;padding:12px;margin:6px 0 12px;
border:1px solid #ded8eb;border-radius:9px;font-size:15px}
button,.btn{background:#7452e8;color:white;border:0;border-radius:9px;
padding:12px 15px;cursor:pointer;text-decoration:none;display:inline-block}
.secondary{background:#eee8ff;color:#5638bd}
.danger{background:#fff0f0;color:#b42318}
label{font-size:14px;font-weight:bold}
.stats{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}
.stat{background:#f1ecff;border-radius:12px;padding:15px}
.stat strong{display:block;font-size:22px;margin-top:8px}
table{width:100%;border-collapse:collapse}
td,th{text-align:left;padding:10px 5px;border-bottom:1px solid #eee;
font-size:14px;overflow-wrap:anywhere}
.scroll{overflow-x:auto}
.inline{display:inline}
.small{font-size:13px}
.progress{background:#eee8ff;border-radius:10px;height:9px;overflow:hidden}
.bar{background:#7452e8;height:9px}
@media(max-width:700px){
.grid{grid-template-columns:1fr}
.stats{grid-template-columns:1fr}
header{padding:18px}
h1{font-size:27px}
.card{padding:17px}
}
</style>
</head>
<body>
<header>
 <div class="logo">✦ Planora</div>
 <div class="muted">Your event, organized.</div>
</header>
<main>
{% if not event %}
 <section class="card">
  <h1>Plan your perfect event ✨</h1>
  <p class="muted">Create your event workspace to manage the budget,
  guests and checklist in one place.</p>
  <form method="post" action="/create">
   <label>Event name and type</label>
   <input name="title" placeholder="e.g. Ananya's Birthday" required>
   <label>Location</label>
   <input name="location" placeholder="City or venue" required>
   <label>Expected guests</label>
   <input name="guests" type="number" min="1" value="50" required>
   <label>Total budget (₹)</label>
   <input name="budget" type="number" min="1" step="0.01"
   placeholder="25000" required>
   <button>Create event workspace</button>
  </form>
 </section>
{% else %}
 <h1>{{ event.title }} 🎉</h1>
 <p class="muted">{{ event.location }} · {{ event.guests }} expected guests</p>

 <div class="stats">
  <div class="stat">Total budget<strong>₹{{ "%.2f"|format(event.budget) }}</strong></div>
  <div class="stat">Spent<strong>₹{{ "%.2f"|format(spent) }}</strong></div>
  <div class="stat">Remaining<strong>₹{{ "%.2f"|format(event.budget-spent) }}</strong></div>
 </div>

 <div class="card" style="margin-top:18px">
  <p class="muted small">Budget used: {{ "%.1f"|format(percent) }}%</p>
  <div class="progress"><div class="bar" style="width:{{ percent }}%"></div></div>
  <p><a class="btn secondary" href="/download">Download event report ↓</a></p>
 </div>

 <div class="grid">
  <section class="card">
   <h2>💸 Expense tracker</h2>
   <form method="post" action="/expense">
    <label>Category</label>
    <select name="category">
     <option>Venue</option><option>Food & Drinks</option>
     <option>Decorations</option><option>Photography</option>
     <option>Entertainment</option><option>Transport</option>
     <option>Other</option>
    </select>
    <label>Description</label>
    <input name="description" placeholder="e.g. Venue advance" required>
    <label>Amount (₹)</label>
    <input name="amount" type="number" min="0.01" step="0.01" required>
    <button>Add expense</button>
   </form>
   <div class="scroll"><table>
    <tr><th>Expense</th><th>Amount</th><th></th></tr>
    {% for x in expenses %}
    <tr><td>{{ x.category }}<br><span class="muted">{{ x.description }}</span></td>
    <td>₹{{ "%.2f"|format(x.amount) }}</td>
    <td><form method="post" action="/expense/{{ x.id }}" class="inline">
    <input type="hidden" name="_method" value="delete">
    <button class="danger" aria-label="Delete expense">×</button></form></td></tr>
    {% else %}<tr><td colspan="3">No expenses added yet.</td></tr>{% endfor %}
   </table></div>
  </section>

  <section class="card">
   <h2>👥 Guest list</h2>
   <form method="post" action="/guest">
    <label>Guest name</label>
    <input name="name" placeholder="Full name" required>
    <label>Contact (optional)</label>
    <input name="contact" placeholder="Phone or email">
    <label>RSVP</label>
    <select name="rsvp"><option>Pending</option>
    <option>Confirmed</option><option>Declined</option></select>
    <button>Add guest</button>
   </form>
   <p class="muted small">{{ confirmed }} confirmed · {{ pending }} pending · {{ declined }} declined</p>
   <div class="scroll"><table>
    <tr><th>Name</th><th>RSVP</th><th></th></tr>
    {% for g in guests %}
    <tr><td>{{ g.name }}<br><span class="muted">{{ g.contact }}</span></td>
    <td>
     <form method="post" action="/guest/{{ g.id }}">
      <select name="rsvp" onchange="this.form.submit()">
       {% for s in ['Pending','Confirmed','Declined'] %}
       <option {% if g.rsvp==s %}selected{% endif %}>{{ s }}</option>
       {% endfor %}
      </select>
     </form>
    </td>
    <td><form method="post" action="/guest/{{ g.id }}/delete">
    <button class="danger">×</button></form></td></tr>
    {% else %}<tr><td colspan="3">No guests added yet.</td></tr>{% endfor %}
   </table></div>
  </section>

  <section class="card">
   <h2>✅ Task checklist</h2>
   <form method="post" action="/task">
    <label>Task</label>
    <input name="title" placeholder="e.g. Confirm the venue" required>
    <label>Due date (optional)</label>
    <input name="due_date" type="date">
    <button>Add task</button>
   </form>
   <p class="muted small">{{ completed }} of {{ tasks|length }} tasks completed</p>
   {% for t in tasks %}
   <div style="padding:10px 0;border-bottom:1px solid #eee">
    <form method="post" action="/task/{{ t.id }}" class="inline">
     <input type="hidden" name="done" value="{{ 0 if t.done else 1 }}">
     <button class="secondary">{{ '✓' if t.done else '○' }}</button>
    </form>
    <span {% if t.done %}style="text-decoration:line-through;color:#888"{% endif %}>
    {{ t.title }}</span>
    {% if t.due_date %}<span class="muted small"> · {{ t.due_date }}</span>{% endif %}
    <form method="post" action="/task/{{ t.id }}/delete" class="inline">
     <button class="danger">×</button>
    </form>
   </div>
   {% else %}<p class="muted">Add your first task above.</p>{% endfor %}
  </section>

  <section class="card">
   <h2>📋 Event summary</h2>
   <p><b>Event:</b> {{ event.title }}</p>
   <p><b>Location:</b> {{ event.location }}</p>
   <p><b>Expected guests:</b> {{ event.guests }}</p>
   <p><b>Budget:</b> ₹{{ "%.2f"|format(event.budget) }}</p>
   <p><b>Recorded expenses:</b> {{ expenses|length }}</p>
   <p><b>Guests on list:</b> {{ guests|length }}</p>
   <p><b>Open tasks:</b> {{ tasks|length-completed }}</p>
   <a class="btn" href="/download">Download full report</a>
   <form method="post" action="/reset" style="margin-top:15px"
   onsubmit="return confirm('Delete this event and all its records?')">
    <button class="danger">Delete this event</button>
   </form>
  </section>
 </div>
{% endif %}
</main>
</body>
</html>
"""


@app.route("/")
def home():
    event = current_event()
    if not event:
        return render_template_string(HTML, event=None)

    eid = event["id"]
    with connect() as db:
        expenses = db.execute(
            "SELECT * FROM expenses WHERE event_id=? ORDER BY id DESC", (eid,)
        ).fetchall()
        guests = db.execute(
            "SELECT * FROM guests WHERE event_id=? ORDER BY id DESC", (eid,)
        ).fetchall()
        tasks = db.execute(
            "SELECT * FROM tasks WHERE event_id=? ORDER BY id DESC", (eid,)
        ).fetchall()

    spent = sum(x["amount"] for x in expenses)
    confirmed = sum(g["rsvp"] == "Confirmed" for g in guests)
    pending = sum(g["rsvp"] == "Pending" for g in guests)
    declined = sum(g["rsvp"] == "Declined" for g in guests)
    completed = sum(t["done"] for t in tasks)
    percent = min(100, spent / event["budget"] * 100) if event["budget"] else 0

    return render_template_string(
        HTML, event=event, expenses=expenses, guests=guests, tasks=tasks,
        spent=spent, percent=percent, confirmed=confirmed, pending=pending,
        declined=declined, completed=completed
    )


@app.post("/create")
def create():
    import uuid
    title = request.form.get("title", "").strip()
    location = request.form.get("location", "").strip()
    try:
        guests = int(request.form["guests"])
        budget = float(request.form["budget"])
        if not title or not location or guests < 1 or budget <= 0:
            raise ValueError
    except (ValueError, KeyError):
        return "Please enter valid event details.", 400

    eid = uuid.uuid4().hex
    with connect() as db:
        db.execute(
            "INSERT INTO events VALUES (?, ?, ?, ?, ?)",
            (eid, title, location, guests, budget)
        )
    session["event_id"] = eid
    return redirect(url_for("home"))


@app.post("/expense")
def add_expense():
    event = current_event()
    if not event:
        return redirect(url_for("home"))
    try:
        amount = float(request.form["amount"])
        description = request.form["description"].strip()
        category = request.form["category"]
        if amount <= 0 or not description:
            raise ValueError
    except (ValueError, KeyError):
        return "Please enter a valid expense.", 400
    with connect() as db:
        db.execute(
            "INSERT INTO expenses(event_id,category,description,amount) VALUES(?,?,?,?)",
            (event["id"], category, description, amount)
        )
    return redirect(url_for("home"))


@app.post("/expense/<int:item_id>")
def delete_expense(item_id):
    event = current_event()
    if event:
        with connect() as db:
            db.execute("DELETE FROM expenses WHERE id=? AND event_id=?",
                       (item_id, event["id"]))
    return redirect(url_for("home"))


@app.post("/guest")
def add_guest():
    event = current_event()
    name = request.form.get("name", "").strip()
    if not event or not name:
        return "Please enter a guest name.", 400
    rsvp = request.form.get("rsvp", "Pending")
    if rsvp not in ("Pending", "Confirmed", "Declined"):
        rsvp = "Pending"
    with connect() as db:
        db.execute(
            "INSERT INTO guests(event_id,name,contact,rsvp) VALUES(?,?,?,?)",
            (event["id"], name, request.form.get("contact", "").strip(), rsvp)
        )
    return redirect(url_for("home"))


@app.post("/guest/<int:item_id>")
def update_guest(item_id):
    event = current_event()
    rsvp = request.form.get("rsvp", "Pending")
    if event and rsvp in ("Pending", "Confirmed", "Declined"):
        with connect() as db:
            db.execute("UPDATE guests SET rsvp=? WHERE id=? AND event_id=?",
                       (rsvp, item_id, event["id"]))
    return redirect(url_for("home"))


@app.post("/guest/<int:item_id>/delete")
def delete_guest(item_id):
    event = current_event()
    if event:
        with connect() as db:
            db.execute("DELETE FROM guests WHERE id=? AND event_id=?",
                       (item_id, event["id"]))
    return redirect(url_for("home"))


@app.post("/task")
def add_task():
    event = current_event()
    title = request.form.get("title", "").strip()
    if not event or not title:
        return "Please enter a task.", 400
    with connect() as db:
        db.execute(
            "INSERT INTO tasks(event_id,title,due_date) VALUES(?,?,?)",
            (event["id"], title, request.form.get("due_date", ""))
        )
    return redirect(url_for("home"))


@app.post("/task/<int:item_id>")
def toggle_task(item_id):
    event = current_event()
    try:
        done = int(request.form["done"])
        if done not in (0, 1):
            raise ValueError
    except (ValueError, KeyError):
        return "Invalid task status.", 400
    if event:
        with connect() as db:
            db.execute("UPDATE tasks SET done=? WHERE id=? AND event_id=?",
                       (done, item_id, event["id"]))
    return redirect(url_for("home"))


@app.post("/task/<int:item_id>/delete")
def delete_task(item_id):
    event = current_event()
    if event:
        with connect() as db:
            db.execute("DELETE FROM tasks WHERE id=? AND event_id=?",
                       (item_id, event["id"]))
    return redirect(url_for("home"))


@app.get("/download")
def download():
    event = current_event()
    if not event:
        return redirect(url_for("home"))

    with connect() as db:
        expenses = db.execute(
            "SELECT * FROM expenses WHERE event_id=?", (event["id"],)
        ).fetchall()
        guests = db.execute(
            "SELECT * FROM guests WHERE event_id=?", (event["id"],)
        ).fetchall()
        tasks = db.execute(
            "SELECT * FROM tasks WHERE event_id=?", (event["id"],)
        ).fetchall()

    spent = sum(x["amount"] for x in expenses)
    lines = [
        "PLANORA - EVENT REPORT",
        "=" * 35,
        f"Event: {event['title']}",
        f"Location: {event['location']}",
        f"Expected guests: {event['guests']}",
        f"Budget: INR {event['budget']:.2f}",
        f"Total expenses: INR {spent:.2f}",
        f"Budget remaining: INR {event['budget']-spent:.2f}",
        "", "EXPENSES", "-" * 20
    ]
    for x in expenses:
        lines.append(
            f"{x['category']} - {x['description']}: INR {x['amount']:.2f}"
        )
    lines += ["", "GUEST LIST", "-" * 20]
    for g in guests:
        lines.append(f"{g['name']} | {g['contact']} | RSVP: {g['rsvp']}")
    lines += ["", "TASK CHECKLIST", "-" * 20]
    for t in tasks:
        lines.append(
            f"[{'x' if t['done'] else ' '}] {t['title']} "
            f"(Due: {t['due_date'] or 'Not set'})"
        )

    data = io.BytesIO(("\n".join(lines)).encode("utf-8"))
    data.seek(0)
    return send_file(
        data, as_attachment=True, download_name="planora_event_report.txt",
        mimetype="text/plain"
    )


@app.post("/reset")
def reset():
    event = current_event()
    if event:
        with connect() as db:
            for table in ("expenses", "guests", "tasks"):
                db.execute(f"DELETE FROM {table} WHERE event_id=?",
                           (event["id"],))
            db.execute("DELETE FROM events WHERE id=?", (event["id"],))
    session.pop("event_id", None)
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run()
