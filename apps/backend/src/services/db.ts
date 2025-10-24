import { Pool } from "pg";
import dotenv from "dotenv";
import { mockDb } from "./mock-db.js";

dotenv.config();

let db: any;

if (process.env.DATABASE_URL) {
  // Use real PostgreSQL database
  db = new Pool({ 
    connectionString: process.env.DATABASE_URL,
    ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false
  });

  // Test connection on startup
  db.connect()
    .then((client: any) => {
      console.log('PostgreSQL database connected successfully');
      client.release();
    })
    .catch((err: any) => {
      console.error('Database connection error:', err.message);
    });
} else {
  // Use mock database for development
  console.log('Using mock database for development (no DATABASE_URL provided)');
  db = mockDb;
}

export { db };
