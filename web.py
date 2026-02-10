import asyncio
import asyncpg
from flask import Flask, render_template_string
from config import Config
from datetime import datetime

app = Flask(__name__)

# ─────────────────────────────────────────
# Database helper (SYNC-SAFE)
# ─────────────────────────────────────────

def run_db_query(coro):
    """
    Runs async DB code safely inside Flask
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


async def fetch_stats():
    conn = await asyncpg.connect(Config.DATABASE_URL)
    try:
        users = await conn.fetchval("SELECT COUNT(*) FROM users")
        reps_total = await conn.fetchval("SELECT COUNT(*) FROM reputation")
        reps_pos = await conn.fetchval(
            "SELECT COUNT(*) FROM reputation WHERE value = 1"
        )
        reps_neg = await conn.fetchval(
            "SELECT COUNT(*) FROM reputation WHERE value = -1"
        )
        return users, reps_total, reps_pos, reps_neg
    finally:
        await conn.close()


# ─────────────────────────────────────────
# Dashboard Route
# ─────────────────────────────────────────

@app.route("/")
def dashboard():
    users, reps_total, reps_pos, reps_neg = run_db_query(fetch_stats())

    return render_template_string(
        DASHBOARD_HTML,
        bot_name=Config.BOT_NAME,
        owner=Config.OWNER_NAME,
        users=users,
        reps_total=reps_total,
        reps_pos=reps_pos,
        reps_neg=reps_neg,
        now=datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
    )


# ─────────────────────────────────────────
# HTML TEMPLATE (INLINE, CLEAN)
# ─────────────────────────────────────────

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{{ bot_name }}</title>
    <style>
        body {
            background: #0f0f12;
            color: #eaeaf0;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, sans-serif;
            margin: 0;
            padding: 40px;
        }

        h1 {
            font-size: 32px;
            margin-bottom: 5px;
        }

        .subtitle {
            opacity: 0.6;
            margin-bottom: 30px;
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 20px;
        }

        .card {
            background: #16161d;
            border-radius: 14px;
            padding: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.25);
        }

        .card span {
            opacity: 0.6;
            font-size: 14px;
        }

        .card strong {
            display: block;
            font-size: 28px;
            margin-top: 8px;
        }

        footer {
            margin-top: 50px;
            opacity: 0.5;
            font-size: 13px;
            text-align: center;
        }
    </style>
</head>
<body>

    <h1>🐼 {{ bot_name }}</h1>
    <div class="subtitle">
        Designed by {{ owner }} · Updated {{ now }}
    </div>

    <div class="grid">
        <div class="card">
            <span>👥 Total Users</span>
            <strong>{{ users }}</strong>
        </div>

        <div class="card">
            <span>➕➖ Total Reputation</span>
            <strong>{{ reps_total }}</strong>
        </div>

        <div class="card">
            <span>➕ Positive</span>
            <strong>{{ reps_pos }}</strong>
        </div>

        <div class="card">
            <span>➖ Negative</span>
            <strong>{{ reps_neg }}</strong>
        </div>
    </div>

    <footer>
        Hello Panda · Calm communities, clear signals 🐾
    </footer>

</body>
</html>
"""


# ─────────────────────────────────────────
# Run Server
# ─────────────────────────────────────────

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8000,
        debug=True
    )
