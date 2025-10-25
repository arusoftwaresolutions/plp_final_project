import { Pool } from "pg";
import dotenv from "dotenv";
import { mockDb } from "./mock-db.js";

dotenv.config();

let db: any;

if (process.env.DATABASE_URL && process.env.DATABASE_URL.trim() !== '') {
  // Use real PostgreSQL database for production
  console.log('Connecting to PostgreSQL database...');
  db = new Pool({ 
    connectionString: process.env.DATABASE_URL,
    ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false
  });

  // Test connection on startup
  db.connect()
    .then((client: any) => {
      console.log('✅ PostgreSQL database connected successfully');
      client.release();
    })
    .catch((err: any) => {
      console.error('❌ Database connection error:', err.message);
      console.log('⚠️  Falling back to mock database for this session');
      // Don't crash the app, fall back to mock DB
      db = mockDb;
    });
} else {
  // Use mock database for development
  console.log('⚠️  Using mock database (no DATABASE_URL provided)');
  db = mockDb;
}

export { db };
