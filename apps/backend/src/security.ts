import type { CorsOptions } from "cors";

const allowed = (process.env.FRONTEND_URL || "").split(",").map((s) => s.trim()).filter(Boolean);

export const corsOptions: CorsOptions = {
  origin: (origin, cb) => {
    if (!origin) return cb(null, true);
    if (allowed.length === 0 || allowed.includes(origin)) return cb(null, true);
    cb(new Error("Not allowed by CORS"));
  },
  credentials: true,
};
