import { createClient } from "redis";
import dotenv from "dotenv";
dotenv.config();

const url = process.env.REDIS_URL || "";
export const redis = createClient({ url });
redis.on("error", (err) => console.error("Redis Error", err));
if (url) {
  redis.connect().catch((e) => console.error("Redis connect error", e));
}
