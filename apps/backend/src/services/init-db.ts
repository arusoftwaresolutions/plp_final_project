import { db } from "./db.js";

// Helper function to check if a table exists
async function tableExists(tableName: string): Promise<boolean> {
  try {
    const result = await db.query(`
      SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = $1
      )
    `, [tableName]);
    return result.rows[0].exists;
  } catch (error) {
    console.warn(`Error checking if table ${tableName} exists:`, error);
    return false;
  }
}

// Helper function to check if extension exists
async function extensionExists(extensionName: string): Promise<boolean> {
  try {
    const result = await db.query(`
      SELECT EXISTS(
        SELECT 1 FROM pg_extension WHERE extname = $1
      )
    `, [extensionName]);
    return result.rows[0].exists;
  } catch (error) {
    console.warn(`Error checking extension ${extensionName}:`, error);
    return false;
  }
}

export async function initializeDatabase() {
  try {
    console.log("🔍 Checking database state...");

    // Check and create PostGIS extension
    const hasPostGIS = await extensionExists('postgis');
    if (!hasPostGIS) {
      await db.query("CREATE EXTENSION IF NOT EXISTS postgis");
      console.log("✅ PostGIS extension created");
    } else {
      console.log("✅ PostGIS extension already exists");
    }

    // Check and create each table individually
    const tables = [
      {
        name: 'users',
        sql: `
          CREATE TABLE users (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            region_code TEXT,
            created_at TIMESTAMP DEFAULT NOW()
          )
        `
      },
      {
        name: 'households',
        sql: `
          CREATE TABLE households (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            household_size INTEGER NOT NULL,
            monthly_income INTEGER NOT NULL
          )
        `
      },
      {
        name: 'transactions',
        sql: `
          CREATE TABLE transactions (
            id SERIAL PRIMARY KEY,
            household_id INTEGER REFERENCES households(id) ON DELETE CASCADE,
            type TEXT NOT NULL,
            category TEXT NOT NULL,
            amount INTEGER NOT NULL
          )
        `
      },
      {
        name: 'regions',
        sql: `
          CREATE TABLE regions (
            id SERIAL PRIMARY KEY,
            region_code TEXT UNIQUE,
            name TEXT,
            geom geometry(MultiPolygon, 4326)
          )
        `
      },
      {
        name: 'poverty_aggregate',
        sql: `
          CREATE TABLE poverty_aggregate (
            id SERIAL PRIMARY KEY,
            region_code TEXT,
            poverty_index NUMERIC
          )
        `
      }
    ];

    for (const table of tables) {
      const exists = await tableExists(table.name);
      if (!exists) {
        await db.query(table.sql);
        console.log(`✅ Created table: ${table.name}`);
      } else {
        console.log(`✅ Table already exists: ${table.name}`);
      }
    }

    // Check and insert sample data only if needed
    const usersExist = await tableExists('users');
    if (usersExist) {
      const userCheck = await db.query("SELECT COUNT(*) FROM users");
      const userCount = parseInt(userCheck.rows[0].count);

      if (userCount === 0) {
        console.log("📝 Inserting sample data...");
        
        // Insert sample user
        await db.query("INSERT INTO users (name, region_code) VALUES ('Araya', 'ET-MK')");
        console.log("✅ Sample user inserted");
        
        // Check if households table exists and insert household
        const householdsExist = await tableExists('households');
        if (householdsExist) {
          await db.query("INSERT INTO households (user_id, household_size, monthly_income) VALUES (1, 4, 3000)");
          console.log("✅ Sample household inserted");
          
          // Check if transactions table exists and insert transactions
          const transactionsExist = await tableExists('transactions');
          if (transactionsExist) {
            await db.query(`
              INSERT INTO transactions (household_id, type, category, amount) VALUES
              (1, 'recurring', 'rent', 1000),
              (1, 'recurring', 'food', 1200),
              (1, 'variable', 'transport', 200),
              (1, 'variable', 'phone', 150),
              (1, 'variable', 'school', 150)
            `);
            console.log("✅ Sample transactions inserted");
          }
        }
      } else {
        console.log(`✅ Sample data already exists (${userCount} users found)`);
      }
    }

    console.log("🎉 Database initialization complete!");

  } catch (error) {
    console.error("❌ Database initialization failed:", error instanceof Error ? error.message : error);
    console.error("⚠️  Application will continue without database initialization");
    // Don't throw error - let the app continue even if DB init fails
  }
}
