from flask import Flask, render_template_string
from config import Config
from datetime import datetime, date, timedelta
import psycopg
import time

app = Flask(__name__)
START_TIME = time.time()

# ─────────────────────────────────────────
# DB CONNECTION
# ─────────────────────────────────────────

def get_conn():
    return psycopg.connect(Config.DATABASE_URL, autocommit=True)

# ─────────────────────────────────────────
# CACHE
# ─────────────────────────────────────────

CACHE = {}
CACHE_TTL = 2.0

def cached(key, fetcher):
    now = time.time()
    if key in CACHE:
        value, ts = CACHE[key]
        if now - ts < CACHE_TTL:
            return value, True
    value = fetcher()
    CACHE[key] = (value, now)
    return value, False

# ─────────────────────────────────────────
# DATA FETCH
# ─────────────────────────────────────────

def fetch_dashboard_data():
    t0 = time.time()

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM users")
            users = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM users WHERE joined_at::date = %s", (date.today(),))
            new_today = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM users WHERE joined_at >= %s", (date.today() - timedelta(days=7),))
            new_week = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM reputation")
            reps_total = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM reputation WHERE created_at::date = %s", (date.today(),))
            reps_today = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM reputation WHERE created_at >= %s", (date.today() - timedelta(days=7),))
            reps_week = cur.fetchone()[0]

            cur.execute("""
                SELECT
                    u.user_id,
                    u.username,
                    COUNT(r.id) AS score
                FROM reputation r
                JOIN users u ON u.user_id = r.receiver
                WHERE r.value = 1
                GROUP BY u.user_id, u.username
                ORDER BY score DESC
                LIMIT 5
            """)
            top_users = cur.fetchall()

            cur.execute("""
                SELECT user_id, username, joined_at
                FROM users
                ORDER BY joined_at DESC
                LIMIT 5
            """)
            recent_joins = cur.fetchall()

            cur.execute("""
                SELECT
                    g.user_id, g.username,
                    rcv.user_id, rcv.username,
                    r.value
                FROM reputation r
                JOIN users g ON g.user_id = r.giver
                JOIN users rcv ON rcv.user_id = r.receiver
                ORDER BY r.created_at DESC
                LIMIT 5
            """)
            recent_reps = cur.fetchall()

    return {
        "users": users,
        "new_today": new_today,
        "new_week": new_week,
        "reps_total": reps_total,
        "reps_today": reps_today,
        "reps_week": reps_week,
        "top_users": top_users,
        "recent_joins": recent_joins,
        "recent_reps": recent_reps,
        "query_ms": int((time.time() - t0) * 1000)
    }

# ─────────────────────────────────────────
# ROUTE
# ─────────────────────────────────────────

@app.route("/")
def dashboard():
    data, cache_hit = cached("dashboard", fetch_dashboard_data)

    uptime = int(time.time() - START_TIME)

    return render_template_string(
        DASHBOARD_HTML,
        bot_name=Config.BOT_NAME,
        owner=Config.OWNER_NAME,
        now=datetime.utcnow().strftime("%d %b %Y · %H:%M UTC"),
        uptime=uptime,
        cache_hit=cache_hit,
        **data
    )

# ─────────────────────────────────────────
# TEMPLATE
# ─────────────────────────────────────────

DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
<title>{{ bot_name }}</title>
<style>
body { background:#0f0f12; color:#eaeaf0; font-family:Inter,system-ui,sans-serif; padding:40px; }
h1 { font-size:36px; }
.status { background:#1e2b1e; color:#7cff9a; padding:6px 14px; border-radius:999px; display:inline-block; }
.grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:20px; margin-top:30px; }
.card { background:#16161d; border-radius:16px; padding:22px; }
.card span { opacity:.6; font-size:13px; }
.card strong { display:block; font-size:28px; margin-top:6px; }
.section { margin-top:50px; }
ul { list-style:none; padding:0; }
li { background:#16161d; padding:12px 16px; border-radius:12px; margin-bottom:8px; display:flex; justify-content:space-between; }
footer { margin-top:60px; text-align:center; opacity:.5; font-size:13px; }
.small { opacity:.6; font-size:12px; }
</style>
</head>
<body>

<h1>🐼 {{ bot_name }}</h1>
<div class="status">● Online</div>
<div class="small">Designed by {{ owner }} · Updated {{ now }}</div>

<div class="grid">
    <div class="card"><span>Total Users</span><strong>{{ users }}</strong></div>
    <div class="card"><span>New Today</span><strong>{{ new_today }}</strong></div>
    <div class="card"><span>New This Week</span><strong>{{ new_week }}</strong></div>
    <div class="card"><span>Total Reputation</span><strong>{{ reps_total }}</strong></div>
    <div class="card"><span>Reputation Today</span><strong>{{ reps_today }}</strong></div>
    <div class="card"><span>Reputation This Week</span><strong>{{ reps_week }}</strong></div>
</div>

<div class="section">
<h2>🌟 Top Appreciated</h2>
<ul>
{% for u in top_users %}
<li><span>User {{ u[0] }}</span><strong>+{{ u[1] }}</strong></li>
{% else %}<li>No data</li>{% endfor %}
</ul>
</div>

<div class="section">
<h2>🆕 Recent Activity</h2>
<ul>
{% for j in recent_joins %}
<li><span>User {{ j[0] }}</span><span>Joined</span></li>
{% endfor %}
{% for r in recent_reps %}
<li><span>{{ r[0] }} → {{ r[1] }}</span><span>{% if r[2]==1 %}+{% else %}-{% endif %}</span></li>
{% endfor %}
</ul>
</div>

<footer>
Uptime: {{ uptime }}s · Query: {{ query_ms }}ms · Cache: {{ "HIT" if cache_hit else "MISS" }}<br>
Hello Panda · Calm communities, clear signals 🐾
</footer>

</body>
</html>
"""

# ─────────────────────────────────────────
# RUN
# ─────────────────────────────────────────

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
