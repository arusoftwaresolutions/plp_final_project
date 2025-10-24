import { Router } from "express";
import jwt from "jsonwebtoken";
import { redis } from "../services/redis.js";
import { z } from "zod";

export const router = Router();

router.post("/request-otp", async (req, res) => {
  const schema = z.object({ email: z.string().email() });
  const parsed = schema.safeParse(req.body);
  if (!parsed.success) return res.status(400).json({ error: "Invalid payload" });
  const { email } = parsed.data;
  const code = Math.floor(100000 + Math.random() * 900000).toString();
  await redis.setEx(`otp:${email}`, 300, code);
  // In production, send via email/SMS. Do NOT return code.
  res.json({ message: "OTP sent" });
});

router.post("/verify-otp", async (req, res) => {
  const schema = z.object({ email: z.string().email(), code: z.string().length(6) });
  const parsed = schema.safeParse(req.body);
  if (!parsed.success) return res.status(400).json({ error: "Invalid payload" });
  const { email, code } = parsed.data;
  const stored = await redis.get(`otp:${email}`);
  if (!stored || stored !== code) return res.status(401).json({ error: "Invalid code" });
  const token = jwt.sign({ sub: email }, process.env.JWT_SECRET as string, { expiresIn: "7d" });
  res.json({ token });
});
