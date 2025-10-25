import { Router } from "express";
import { db } from "../services/db.js";
import { generateAdvice } from "../services/ai.js";

export const router = Router();

router.get("/budget/:householdId", async (req, res) => {
  const id = Number(req.params.householdId);
  if (!Number.isFinite(id)) return res.status(400).json({ error: "Invalid householdId" });

  // Gather household income and expenses
  const hh = await db.query(
    "SELECT h.id, h.monthly_income, h.household_size, u.name FROM households h JOIN users u ON u.id=h.user_id WHERE h.id=$1",
    [id]
  );
  if (hh.rowCount === 0) return res.status(404).json({ error: "Household not found" });

  const tx = await db.query(
    "SELECT type, category, amount FROM transactions WHERE household_id=$1",
    [id]
  );

  const advice = await generateAdvice({
    household: hh.rows[0],
    transactions: tx.rows,
  });

  // Return only human text to the UI
  res.json({ advice });
});

// General AI chat endpoint for contextual responses
router.post("/chat/:householdId", async (req, res) => {
  const id = Number(req.params.householdId);
  if (!Number.isFinite(id)) return res.status(400).json({ error: "Invalid householdId" });
  
  const { message } = req.body;
  if (!message || typeof message !== 'string') {
    return res.status(400).json({ error: "Message is required" });
  }

  try {
    // Get household context
    const hh = await db.query(
      "SELECT h.id, h.monthly_income, h.household_size, u.name FROM households h JOIN users u ON u.id=h.user_id WHERE h.id=$1",
      [id]
    );
    
    if (hh.rowCount === 0) {
      return res.status(404).json({ error: "Household not found" });
    }

    const tx = await db.query(
      "SELECT type, category, amount FROM transactions WHERE household_id=$1",
      [id]
    );

    // Generate contextual advice based on user's message and their financial data
    const advice = await generateAdvice({
      household: hh.rows[0],
      transactions: tx.rows,
      userMessage: message
    });

    res.json({ response: advice });
  } catch (error) {
    console.error('AI Chat error:', error);
    res.status(500).json({ error: "Failed to generate response" });
  }
});
