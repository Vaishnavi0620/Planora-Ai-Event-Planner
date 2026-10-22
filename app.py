
from flask import Flask, request, render_template_string

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Planora AI Event Planner</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f4f1ff;
            color: #282044;
            max-width: 650px;
            margin: 40px auto;
            padding: 20px;
        }
        .card {
            background: white;
            padding: 28px;
            border-radius: 16px;
            box-shadow: 0 4px 20px #0001;
        }
        input, select, button {
            box-sizing: border-box;
            width: 100%;
            padding: 12px;
            margin: 8px 0 16px;
            border-radius: 8px;
            border: 1px solid #ccc;
        }
        button {
            background: #6d4aff;
            color: white;
            border: none;
            cursor: pointer;
        }
        h1 { color: #6d4aff; }
    </style>
</head>
<body>
<div class="card">
    <h1>Planora ✨</h1>
    <p>Your personal event planning assistant</p>
    <form method="POST">
        <label>Event type</label>
        <select name="event" required>
            <option>Wedding</option>
            <option>Birthday</option>
            <option>Community Event</option>
            <option>Anniversary</option>
        </select>
        <label>Location</label>
        <input name="location" placeholder="Enter event location" required>
        <label>Number of guests</label>
        <input name="guests" type="number" min="1"
               placeholder="e.g. 100" required>
        <label>Budget</label>
        <input name="budget" type="number" min="1"
               placeholder="Budget in INR" required>
        <button type="submit">Create My Event Plan</button>
    </form>
    {% if plan %}
        <hr>
        <h2>Your Event Plan</h2>
        <p><b>Event:</b> {{ plan.event }}</p>
        <p><b>Location:</b> {{ plan.location }}</p>
        <p><b>Guests:</b> {{ plan.guests }}</p>
        <p><b>Budget:</b> ₹{{ plan.budget }}</p>
        <h3>Suggested checklist</h3>
        <ul>
            <li>Choose a venue and confirm availability.</li>
            <li>Plan food and refreshments.</li>
            <li>Arrange decorations and seating.</li>
            <li>Prepare invitations and guest list.</li>
            <li>Confirm vendors and event schedule.</li>
        </ul>
        <p>Keep your expenses within your planned budget.</p>
    {% endif %}
</div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    plan = None

    if request.method == "POST":
        plan = {
            "event": request.form["event"],
            "location": request.form["location"],
            "guests": int(request.form["guests"]),
            "budget": float(request.form["budget"]),
        }

    return render_template_string(HTML, plan=plan)

if __name__ == "__main__":
    app.run()
