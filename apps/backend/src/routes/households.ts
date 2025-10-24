import { Router } from "express";
import { z } from "zod";
import { db } from "../services/db.js";

export const router = Router();

// Create household
router.post("/", async (req, res) => {
  try {
    const schema = z.object({
      user_id: z.number(),
      household_size: z.number().min(1),
      monthly_income: z.number().min(0)
    });
    
    const parsed = schema.safeParse(req.body);
    if (!parsed.success) {
      return res.status(400).json({ error: "Invalid payload", details: parsed.error.issues });
    }

    const { user_id, household_size, monthly_income } = parsed.data;
    
    const result = await db.query(
      "INSERT INTO households (user_id, household_size, monthly_income) VALUES ($1, $2, $3) RETURNING id, user_id, household_size, monthly_income",
      [user_id, household_size, monthly_income]
    );
    
    res.status(201).json(result.rows[0]);
  } catch (error) {
    console.error('Household creation error:', error);
    res.status(500).json({ error: "Internal server error" });
  }
});

// Get household by user ID
router.get("/user/:userId", async (req, res) => {
  try {
    const userId = parseInt(req.params.userId);
    if (isNaN(userId)) {
      return res.status(400).json({ error: "Invalid user ID" });
    }
    
    const result = await db.query(
      "SELECT id, user_id, household_size, monthly_income FROM households WHERE user_id = $1",
      [userId]
    );
    
    if (result.rows.length === 0) {
      return res.status(404).json({ error: "Household not found" });
    }
    
    res.json(result.rows[0]);
  } catch (error) {
    console.error('Household fetch error:', error);
    res.status(500).json({ error: "Internal server error" });
  }
});