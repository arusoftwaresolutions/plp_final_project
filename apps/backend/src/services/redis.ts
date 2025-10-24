import { createClient } from "redis";
import dotenv from "dotenv";
dotenv.config();

const url = process.env.REDIS_URL?.trim();

// Create a mock redis client if no URL provided
const createMockRedis = () => ({
  set: async () => "OK",
  setEx: async () => "OK",
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
  redis.on("error", (err) => console.error("Redis Error", err));
  (redis as any).connect().catch((e: any) => console.error("Redis connect error", e));
} else {
  console.warn("Redis URL not provided, using mock Redis client");
}
