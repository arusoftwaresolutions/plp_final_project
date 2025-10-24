import { Router } from "express";
import { z } from "zod";
import { db } from "../services/db.js";

export const router = Router();

router.post("/", async (req, res) => {
  const schema = z.object({ name: z.string(), email: z.string().email().optional(), region_code: z.string().optional() });
  const parsed = schema.safeParse(req.body);
  if (!parsed.success) return res.status(400).json({ error: "Invalid payload" });

  const { name, email, region_code } = parsed.data;
  const result = await db.query(
    "INSERT INTO users (name, email, region_code) VALUES ($1, $2, $3) RETURNING id, name, email, region_code",
    [name, email ?? null, region_code ?? null]
  );
  res.status(201).json(result.rows[0]);
});
