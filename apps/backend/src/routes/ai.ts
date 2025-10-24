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
