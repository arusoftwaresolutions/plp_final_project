import { db } from "./db.js";

export async function initializeDatabase() {
  try {
    console.log("Initializing database...");

    // Create PostGIS extension
    await db.query("CREATE EXTENSION IF NOT EXISTS postgis");
    console.log("✅ PostGIS extension ready");

    // Create tables
    await db.query(`
      CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT UNIQUE,
        region_code TEXT
      )
    `);

    await db.query(`
      CREATE TABLE IF NOT EXISTS households (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
        household_size INTEGER NOT NULL,
        monthly_income INTEGER NOT NULL
      )
    `);

    await db.query(`
      CREATE TABLE IF NOT EXISTS transactions (
        id SERIAL PRIMARY KEY,
        household_id INTEGER REFERENCES households(id) ON DELETE CASCADE,
        type TEXT NOT NULL,
        category TEXT NOT NULL,
        amount INTEGER NOT NULL
      )
    `);

    await db.query(`
      CREATE TABLE IF NOT EXISTS regions (
        id SERIAL PRIMARY KEY,
        region_code TEXT UNIQUE,
        name TEXT,
        geom geometry(MultiPolygon, 4326)
      )
    `);

    await db.query(`
      CREATE TABLE IF NOT EXISTS poverty_aggregate (
        id SERIAL PRIMARY KEY,
        region_code TEXT,
        poverty_index NUMERIC
      )
    `);

    console.log("✅ Tables created successfully");

    // Check if sample data already exists
    const userCheck = await db.query("SELECT COUNT(*) FROM users");
    const userCount = parseInt(userCheck.rows[0].count);

    if (userCount === 0) {
      // Insert sample data only if tables are empty
      await db.query("INSERT INTO users (name, region_code) VALUES ('Araya', 'ET-MK')");
      
      await db.query("INSERT INTO households (user_id, household_size, monthly_income) VALUES (1, 4, 3000)");
      
      await db.query(`
        INSERT INTO transactions (household_id, type, category, amount) VALUES
        (1, 'recurring', 'rent', 1000),
        (1, 'recurring', 'food', 1200),
        (1, 'variable', 'transport', 200),
        (1, 'variable', 'phone', 150),
        (1, 'variable', 'school', 150)
      `);

      console.log("✅ Sample data inserted");
    } else {
      console.log("✅ Sample data already exists, skipping insertion");
    }

    console.log("🎉 Database initialization complete!");

  } catch (error) {
    console.error("❌ Database initialization failed:", error instanceof Error ? error.message : error);
    // Don't throw error - let the app continue even if DB init fails
  }
}