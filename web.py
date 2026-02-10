import asyncio
import asyncpg
from flask import Flask, render_template_string
from config import Config
from datetime import datetime, date

app = Flask(__name__)

# ─────────────────────────────────────────
# GLOBAL EVENT LOOP + DB POOL
# ─────────────────────────────────────────

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
db_pool: asyncpg.Pool | None = None


async def init_db():
    global db_pool
    if not db_pool:
        db_pool = await asyncpg.create_pool(
            Config.DATABASE_URL,
            min_size=1,
            max_size=5
        )


def run(coro):
    return loop.run_until_complete(coro)


# ─────────────────────────────────────────
# DATA QUERIES
# ─────────────────────────────────────────

async def fetch_dashboard_data():
    async with db_pool.acquire() as conn:
        users = await conn.fetchval("SELECT COUNT(*) FROM users")

        new_today = await conn.fetchval(
            "SELECT COUNT(*) FROM users WHERE joined_at::date = $1",
            date.today()
        )

        reps_total = await conn.fetchval("SELECT COUNT(*) FROM reputation")

        reps_today = await conn.fetchval(
            "SELECT COUNT(*) FROM reputation WHERE created_at::date = $1",
            date.today()
        )

        top_users = await conn.fetch(
            """
            SELECT receiver, COUNT(*) AS score
            FROM reputation
            WHERE value = 1
            GROUP BY receiver
            ORDER BY score DESC
            LIMIT 5
            """
        )

        return {
            "users": users,
            "new_today": new_today,
            "reps_total": reps_total,
            "reps_today": reps_today,
            "top_users": top_users
        }


# ─────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────

@app.route("/")
def dashboard():
    run(init_db())
    data = run(fetch_dashboard_data())

    return render_template_string(
        DASHBOARD_HTML,
        bot_name=Config.BOT_NAME,
        owner=Config.OWNER_NAME,
        now=datetime.utcnow().strftime("%d %b %Y · %H:%M UTC"),
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
        body {
            background: #0f0f12;
            color: #eaeaf0;
            font-family: Inter, system-ui, sans-serif;
            padding: 40px;
        }

        h1 {
            font-size: 36px;
            margin-bottom: 6px;
        }

        .status {
            display: inline-block;
            background: #1e2b1e;
            color: #7CFF9A;
            padding: 6px 14px;
            border-radius: 999px;
            font-size: 13px;
            margin-bottom: 30px;
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 20px;
        }

        .card {
            background: #16161d;
            border-radius: 16px;
            padding: 22px;
        }

        .card span {
            opacity: 0.6;
            font-size: 13px;
        }

        .card strong {
            display: block;
            font-size: 30px;
            margin-top: 8px;
        }

        .section {
            margin-top: 50px;
        }

        ul {
            list-style: none;
            padding: 0;
        }

        li {
            background: #16161d;
            padding: 14px 18px;
            border-radius: 12px;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
        }

        footer {
            margin-top: 60px;
            text-align: center;
            opacity: 0.5;
            font-size: 13px;
        }
    </style>
</head>

<body>

    <h1>🐼 {{ bot_name }}</h1>
    <div class="status">● Online</div>

    <div class="subtitle">
        Designed by {{ owner }} · Updated {{ now }}
    </div>

    <div class="grid">
        <div class="card">
            <span>Total Users</span>
            <strong>{{ users }}</strong>
        </div>

        <div class="card">
            <span>New Today</span>
            <strong>{{ new_today }}</strong>
        </div>

        <div class="card">
            <span>Total Reputation</span>
            <strong>{{ reps_total }}</strong>
        </div>

        <div class="card">
            <span>Reputation Today</span>
            <strong>{{ reps_today }}</strong>
        </div>
    </div>

    <div class="section">
        <h2>🌟 Top Appreciated Members</h2>
        <ul>
            {% for row in top_users %}
            <li>
                <span>User ID {{ row.receiver }}</span>
                <strong>+{{ row.score }}</strong>
            </li>
            {% else %}
            <li>No data yet</li>
            {% endfor %}
        </ul>
    </div>

    <footer>
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
