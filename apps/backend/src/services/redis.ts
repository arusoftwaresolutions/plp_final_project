import { createClient } from "redis";
import dotenv from "dotenv";
dotenv.config();

const url = process.env.REDIS_URL?.trim();

// Create a mock redis client if no URL provided
const createMockRedis = () => ({
  set: async () => "OK",
  setEx: async () => "OK",
  expire: async () => 1,
  get: async () => null,
  del: async () => 1,
  connect: async () => {},
  disconnect: async () => {},
  on: () => {},
});

export const redis = url && url !== "" 
  ? createClient({ url })
  : createMockRedis();

if (url && url !== "") {
  redis.on("error", (err) => console.error("❌ Redis Error:", err));
  redis.on("connect", () => console.log("✅ Redis connected successfully"));
  (redis as any).connect().catch((e: any) => {
    console.error("❌ Redis connect error:", e);
    console.log("⚠️  Continuing without Redis - using mock client");
  });
} else {
  console.log("⚠️  Redis URL not provided, using mock Redis client");
}
