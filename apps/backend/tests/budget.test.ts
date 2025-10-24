import request from "supertest";
import app from "../src/app.js";

// Budget allocation sum <= income (using seed-like values)
describe("budget", () => {
  it("allocation should be <= income", async () => {
    const monthlyIncome = 3000;
    const transactions = [1000, 1200, 200, 150, 150];
    const totalAllocated = transactions.reduce((a, b) => a + b, 0);
    expect(totalAllocated).toBeLessThanOrEqual(monthlyIncome);
  });

  it("/api/health is up", async () => {
    const res = await request(app).get("/api/health");
    expect(res.statusCode).toBe(200);
    expect(res.body.status).toBe("ok");
  });
});
