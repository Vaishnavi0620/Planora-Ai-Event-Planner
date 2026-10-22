
from flask import Flask, request, render_template_string

app = Flask(__name__)

PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Planora | Plan your perfect event</title>
<style>
:root {
  --purple: #7452e8;
  --dark: #211b38;
  --muted: #77748b;
  --bg: #f8f7fc;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: Inter, Arial, sans-serif;
  color: var(--dark);
  background: var(--bg);
}
nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 22px 7%;
  background: white;
  border-bottom: 1px solid #efedf6;
}
.logo { font-size: 25px; font-weight: 800; color: var(--purple); }
nav a { color: var(--dark); text-decoration: none; margin-left: 24px; }
.pill {
  background: #eee8ff;
  color: var(--purple);
  border-radius: 30px;
  padding: 9px 14px;
  font-size: 13px;
  display: inline-block;
}
.hero {
  padding: 68px 7% 50px;
  background: linear-gradient(120deg, #f1ebff, #fff 65%, #fceeff);
}
.hero h1 {
  font-size: clamp(38px, 6vw, 65px);
  line-height: 1.08;
  letter-spacing: -2px;
  max-width: 700px;
  margin: 22px 0;
}
.hero h1 span { color: var(--purple); }
.hero p { color: var(--muted); font-size: 17px; line-height: 1.8; max-width: 560px; }
main { max-width: 1120px; margin: auto; padding: 35px 22px 70px; }
.section-title { font-size: 28px; margin-bottom: 8px; }
.subtitle { color: var(--muted); margin-bottom: 28px; }
.layout {
  display: grid;
  grid-template-columns: 1.2fr .8fr;
  gap: 24px;
  align-items: start;
}
.card {
  background: white;
  border: 1px solid #eeebf5;
  border-radius: 20px;
  padding: 28px;
  box-shadow: 0 12px 35px #30205b0b;
}
label { display: block; font-size: 14px; font-weight: 650; margin: 17px 0 8px; }
input, select {
  width: 100%;
  padding: 14px;
  border: 1px solid #e3dfed;
  border-radius: 10px;
  background: #fff;
  color: var(--dark);
  font-size: 15px;
  outline-color: var(--purple);
}
button {
  width: 100%;
  margin-top: 23px;
  padding: 15px;
  background: var(--purple);
  color: white;
  border: 0;
  border-radius: 11px;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
}
button:hover { background: #5f40d0; }
.events { display: grid; grid-template-columns: 1fr 1fr; gap: 13px; }
.event {
  padding: 20px 15px;
  border-radius: 15px;
  background: #f5f1ff;
}
.event:nth-child(2) { background: #fff0f5; }
.event:nth-child(3) { background: #edf8f4; }
.event:nth-child(4) { background: #fff5e8; }
.emoji { font-size: 29px; }
.event h3 { font-size: 15px; margin-bottom: 6px; }
.event p { font-size: 13px; line-height: 1.5; color: var(--muted); margin-bottom: 0; }
.result { margin-top: 24px; border-left: 4px solid var(--purple); }
.result li { margin: 12px 0; line-height: 1.5; }
footer { text-align: center; padding: 25px; color: var(--muted); font-size: 13px; }
@media(max-width: 720px) {
  nav { padding: 18px 5%; }
  nav a { margin-left: 10px; font-size: 13px; }
  .hero { padding: 48px 6% 35px; }
  .layout { grid-template-columns: 1fr; }
  .card { padding: 21px; }
  main { padding: 25px 16px 50px; }
}
</style>
</head>
<body>
<nav>
  <div class="logo">✦ Planora</div>
  <div>
    <a href="#explore">Explore</a>
    <a href="#planner">Planner</a>
  </div>
</nav>

<section class="hero">
  <span class="pill">✦ YOUR PERSONAL EVENT ASSISTANT</span>
  <h1>Make every moment <span>unforgettable.</span></h1>
  <p>
    From dream weddings to joyful birthdays, bring your ideas to life
    with a thoughtful event plan made around your style and budget.
  </p>
  <a href="#planner" style="display:inline-block;background:#7452e8;color:white;
  padding:14px 22px;border-radius:10px;text-decoration:none;font-weight:700">
    Plan my event &nbsp; →
  </a>
</section>

<main>
  <section id="explore">
    <h2 class="section-title">Every celebration starts here</h2>
    <p class="subtitle">A little inspiration for your next big moment.</p>
    <div class="events">
      <div class="event"><div class="emoji">💍</div>
        <h3>Dream Weddings</h3><p>Celebrate your love, your way.</p></div>
      <div class="event"><div class="emoji">🎂</div>
        <h3>Birthday Parties</h3><p>Make another year magical.</p></div>
      <div class="event"><div class="emoji">🎉</div>
        <h3>Community Events</h3><p>Bring your people together.</p></div>
      <div class="event"><div class="emoji">🥂</div>
        <h3>Special Occasions</h3><p>Make every milestone count.</p></div>
    </div>
  </section>

  <section id="planner" style="margin-top:45px">
    <h2 class="section-title">Let's plan something wonderful</h2>
    <p class="subtitle">Tell us a few details to get your planning checklist.</p>
    <div class="layout">
      <div class="card">
        <h2 style="margin-top:0">Your event details ✨</h2>
        <form method="POST">
          <label for="event">What are we celebrating?</label>
          <select id="event" name="event" required>
            <option value="Wedding">💍 Wedding</option>
            <option value="Birthday">🎂 Birthday</option>
            <option value="Community Event">🎉 Community event</option>
            <option value="Anniversary">🥂 Anniversary</option>
            <option value="Other">✨ Other occasion</option>
          </select>
          <label for="location">Event location</label>
          <input id="location" name="location" placeholder="City or venue" required>
          <label for="guests">Expected guests</label>
          <input id="guests" name="guests" type="number" min="1"
            max="100000" placeholder="e.g. 100" required>
          <label for="budget">Total budget (₹)</label>
          <input id="budget" name="budget" type="number" min="1"
            placeholder="e.g. 50000" required>
          <button type="submit">Create my event plan →</button>
        </form>
      </div>

      <div>
        <div class="card">
          <span class="pill">YOUR PLANNING COMPANION</span>
          <h2>Big ideas, made simpler.</h2>
          <p style="color:#77748b;line-height:1.8">
            Start with your event essentials and build a plan one step at a time.
          </p>
          <hr style="border:0;border-top:1px solid #eeeaf5;margin:22px 0">
          <p>✓ &nbsp; Organize your priorities</p>
          <p>✓ &nbsp; Keep your budget in view</p>
          <p>✓ &nbsp; Build your preparation checklist</p>
          <p>✓ &nbsp; Plan with more confidence</p>
        </div>

        {% if plan %}
        <div class="card result">
          <h2>Your event plan 🎊</h2>
          <p><b>Event:</b> {{ plan.event }}</p>
          <p><b>Location:</b> {{ plan.location }}</p>
          <p><b>Guests:</b> {{ plan.guests }}</p>
          <p><b>Budget:</b> ₹{{ "{:,.2f}".format(plan.budget) }}</p>
          <h3>Getting started checklist</h3>
          <ul>
            <li>Research venues suitable for your guest count.</li>
            <li>Set aside funds for food, venue and decorations.</li>
            <li>Prepare your guest list and invitations.</li>
            <li>Compare vendors before making bookings.</li>
            <li>Write a schedule for the event day.</li>
          </ul>
          <p><b>Reminder:</b> Confirm actual prices and availability with vendors.</p>
        </div>
        {% endif %}
      </div>
    </div>
  </section>
</main>
<footer>Made with ✦ for life's special moments · Planora</footer>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    plan = None

    if request.method == "POST":
        try:
            guests = int(request.form["guests"])
            budget = float(request.form["budget"])
            if guests < 1 or budget <= 0:
                raise ValueError
            plan = {
                "event": request.form["event"],
                "location": request.form["location"].strip(),
                "guests": guests,
                "budget": budget,
            }
            if not plan["location"]:
                plan = None
        except (ValueError, TypeError):
            plan = None

    return render_template_string(PAGE, plan=plan)

if __name__ == "__main__":
    app.run()
