import { Router } from "express";
import { z } from "zod";
import bcrypt from "bcryptjs";
import { db } from "../services/db.js";

export const router = Router();

// Register new user
router.post("/register", async (req, res) => {
  try {
    const schema = z.object({ 
      name: z.string().min(1), 
      email: z.string().email(), 
      password: z.string().min(6),
      monthlyIncome: z.number().optional(),
      householdSize: z.number().optional()
    });
    
    const parsed = schema.safeParse(req.body);
    if (!parsed.success) {
      return res.status(400).json({ error: "Invalid payload", details: parsed.error.issues });
    }

    const { name, email, password, monthlyIncome = 0, householdSize = 1 } = parsed.data;
    
    // Check if user already exists
    const existingUser = await db.query("SELECT id FROM users WHERE email = $1", [email]);
    if (existingUser.rows.length > 0) {
      return res.status(409).json({ error: "User already exists" });
    }
    
    // Hash password
    const hashedPassword = await bcrypt.hash(password, 10);
    
    // Insert user
    const userResult = await db.query(
      "INSERT INTO users (name, email, password) VALUES ($1, $2, $3) RETURNING id, name, email",
      [name, email, hashedPassword]
    );
    
    const user = userResult.rows[0];
    
    // Always insert household record
    const householdResult = await db.query(
      "INSERT INTO households (user_id, household_size, monthly_income) VALUES ($1, $2, $3) RETURNING id",
      [user.id, householdSize, monthlyIncome]
    );
    
    // Build complete user response
    const completeUser = {
      id: user.id,
      name: user.name,
      email: user.email,
      householdId: householdResult.rows[0].id,
      monthlyIncome,
      householdSize
    };
    
    console.log('Registration successful:', completeUser);
    res.status(201).json(completeUser);
  } catch (error) {
    console.error('Registration error:', error);
    res.status(500).json({ error: "Internal server error" });
  }
});

// Login user
router.post("/login", async (req, res) => {
  try {
    const schema = z.object({ 
      email: z.string().email(), 
      password: z.string()
    });
    
    const parsed = schema.safeParse(req.body);
    if (!parsed.success) {
      return res.status(400).json({ error: "Invalid payload" });
    }

    const { email, password } = parsed.data;
    
    // Find user
    const userResult = await db.query(
      "SELECT id, name, email, password FROM users WHERE email = $1",
      [email]
    );
    
    if (userResult.rows.length === 0) {
      return res.status(401).json({ error: "Invalid credentials" });
    }
    
    const user = userResult.rows[0];
    
    // Check password
    const validPassword = await bcrypt.compare(password, user.password);
    if (!validPassword) {
      return res.status(401).json({ error: "Invalid credentials" });
    }
    
    // Get household info if exists
    const householdResult = await db.query(
      "SELECT id, household_size, monthly_income FROM households WHERE user_id = $1",
      [user.id]
    );
    
    const responseUser = {
      id: user.id,
      name: user.name,
      email: user.email,
      householdId: householdResult.rows[0]?.id || null,
      monthlyIncome: householdResult.rows[0]?.monthly_income || 0,
      householdSize: householdResult.rows[0]?.household_size || 1
    };
    
    console.log('Login successful:', responseUser);
    res.json(responseUser);
  } catch (error) {
    console.error('Login error:', error);
    res.status(500).json({ error: "Internal server error" });
  }
});
