import fs from "fs";
import path from "path";
import dotenv from "dotenv";
import OpenAI from "openai";
dotenv.config();

const root = path.resolve(__dirname, "../../../");
const systemPromptPath = path.join(root, "ai", "system_prompt.txt");
const systemPrompt = fs.readFileSync(systemPromptPath, "utf-8");

const model = process.env.MODEL_NAME || "gpt-4o-mini";
const apiKey = process.env.OPENAI_API_KEY || "";
const openai = apiKey ? new OpenAI({ apiKey }) : null;

type Tx = { type: string; category: string; amount: number };

type AdviceInput = {
  household: { id: number; monthly_income: number; household_size: number; name: string };
  transactions: Tx[];
};

export async function generateAdvice(input: AdviceInput): Promise<string> {
  const income = input.household.monthly_income;
  const lines = input.transactions.map((t) => `${t.category} = ${t.amount}`).join("; ");
  const userPrompt = `Household size ${input.household.household_size}, income = ${income}. Expenses: ${lines}. Provide friendly budgeting tips.`;

  // Fallback advice if AI unavailable
  const fallback = () => {
    const total = input.transactions.reduce((s, t) => s + t.amount, 0);
    const left = Math.max(0, income - total);
    return [
      `You make about ${income.toLocaleString()} ETB each month.`,
      `Rent and food take most of it — that's okay.`,
      `Try buying staples in bulk and reduce small phone costs.`,
      `You could aim to save about ${Math.floor(left * 0.1)} ETB this month.`,
      `Keep going step by step — you're doing great!`,
    ].join(" ");
  };

  if (!openai) return fallback();

  try {
    const chat = await openai.chat.completions.create({
      model,
      messages: [
        { role: "system", content: systemPrompt },
        { role: "user", content: userPrompt },
      ],
      temperature: 0.4,
    });
    const text = chat.choices?.[0]?.message?.content?.trim();
    if (!text) return fallback();
    // Ensure plain text only
    return text.replace(/\{[\s\S]*\}/g, "").trim();
  } catch (e) {
    return fallback();
  }
}
