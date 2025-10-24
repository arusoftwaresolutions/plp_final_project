CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  email TEXT UNIQUE,
  region_code TEXT
);

CREATE TABLE IF NOT EXISTS households (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
  household_size INTEGER NOT NULL,
  monthly_income INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS transactions (
  id SERIAL PRIMARY KEY,
  household_id INTEGER REFERENCES households(id) ON DELETE CASCADE,
  type TEXT NOT NULL,
  category TEXT NOT NULL,
  amount INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS regions (
  id SERIAL PRIMARY KEY,
  region_code TEXT UNIQUE,
  name TEXT,
  geom geometry(MultiPolygon, 4326)
);

-- Aggregated poverty index per region
CREATE TABLE IF NOT EXISTS poverty_aggregate (
  id SERIAL PRIMARY KEY,
  region_code TEXT,
  poverty_index NUMERIC
);
