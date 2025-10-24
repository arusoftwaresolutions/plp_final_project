import { Router } from "express";
import { z } from "zod";
import { db } from "../services/db.js";

export const router = Router();

router.post("/", async (req, res) => {
  const schema = z.object({
    household_id: z.number(),
    type: z.enum(["recurring", "variable"]),
    category: z.string(),
    amount: z.number().nonnegative(),
  });
  const parsed = schema.safeParse(req.body);
  if (!parsed.success) return res.status(400).json({ error: "Invalid payload" });
  const { household_id, type, category, amount } = parsed.data;
  const result = await db.query(
    "INSERT INTO transactions (household_id, type, category, amount) VALUES ($1,$2,$3,$4) RETURNING id, household_id, type, category, amount",
    [household_id, type, category, amount]
  );
  res.status(201).json(result.rows[0]);
});
