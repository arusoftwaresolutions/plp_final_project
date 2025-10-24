import { generateAdvice } from "../src/services/ai.js";

test("AI returns human text, not JSON", async () => {
  const text = await generateAdvice({
    household: { id: 1, monthly_income: 3000, household_size: 4, name: "Test" },
    transactions: [
      { type: "recurring", category: "rent", amount: 1000 },
      { type: "recurring", category: "food", amount: 1200 },
      { type: "variable", category: "transport", amount: 200 },
      { type: "variable", category: "phone", amount: 150 },
      { type: "variable", category: "school", amount: 150 },
    ],
  });
  expect(typeof text).toBe("string");
  expect(text.includes("{")).toBe(false);
});
