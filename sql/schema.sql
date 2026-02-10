CREATE TABLE IF NOT EXISTS users (
  user_id BIGINT PRIMARY KEY,
  joined_at TIMESTAMP DEFAULT NOW()
);

ALTER TABLE users
  ADD COLUMN IF NOT EXISTS username TEXT;

CREATE TABLE IF NOT EXISTS reputation (
  id SERIAL PRIMARY KEY,
  giver BIGINT,
  receiver BIGINT,
  value SMALLINT CHECK (value IN (1, -1)),
  reason TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS cooldowns (
  user_id BIGINT PRIMARY KEY,
  last_action TIMESTAMP
);
