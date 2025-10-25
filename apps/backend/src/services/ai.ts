import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import dotenv from "dotenv";
import OpenAI from "openai";
dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
// Go from backend/dist/services to repo root: ../../../.. (4 levels up)
const root = path.resolve(__dirname, "../../../../");
const systemPromptPath = path.join(root, "ai", "system_prompt.txt");

// Add error handling and fallback
let systemPrompt = "You are a helpful budgeting assistant. Provide clear, practical advice for low-income families.";
try {
  if (fs.existsSync(systemPromptPath)) {
    systemPrompt = fs.readFileSync(systemPromptPath, "utf-8");
  } else {
    console.warn(`System prompt not found at ${systemPromptPath}, using default`);
  }
} catch (error) {
  console.warn(`Failed to read system prompt: ${error instanceof Error ? error.message : 'Unknown error'}, using default`);
}

const model = process.env.MODEL_NAME || "gpt-4o-mini";
const apiKey = process.env.OPENAI_API_KEY || "";
const openai = apiKey ? new OpenAI({ apiKey }) : null;

type Tx = { type: string; category: string; amount: number };

type AdviceInput = {
  household: { id: number; monthly_income: number; household_size: number; name: string };
  transactions: Tx[];
  userMessage?: string;
};

export async function generateAdvice(input: AdviceInput): Promise<string> {
  const income = input.household.monthly_income;
  const lines = input.transactions.map((t) => `${t.category} = ${t.amount}`).join("; ");
  
  let userPrompt;
  if (input.userMessage) {
    userPrompt = `User question: "${input.userMessage}". Context - Household size: ${input.household.household_size}, income: ${income} ETB. Expenses: ${lines}. Please provide personalized financial advice based on their question and financial situation.`;
  } else {
    userPrompt = `Household size ${input.household.household_size}, income = ${income}. Expenses: ${lines}. Provide friendly budgeting tips.`;
  }

  // Fallback advice if AI unavailable
  const fallback = () => {
    const total = input.transactions.reduce((s, t) => s + t.amount, 0);
    const left = Math.max(0, income - total);
    
    if (input.userMessage) {
      // Provide contextual fallback based on user question
      if (input.userMessage.toLowerCase().includes('budget')) {
        return `Based on your ${income.toLocaleString()} ETB income and current expenses, I recommend the 50/30/20 rule: 50% for needs, 30% for wants, and 20% for savings. You have about ${left} ETB left after expenses. Would you like specific budget categories?`;
      } else if (input.userMessage.toLowerCase().includes('save')) {
        return `With your income of ${income.toLocaleString()} ETB, try to save at least ${Math.floor(left * 0.2)} ETB monthly. Start small - even 100 ETB per month builds good habits. Consider reducing variable expenses first.`;
      } else if (input.userMessage.toLowerCase().includes('debt')) {
        return `For debt management with ${income.toLocaleString()} ETB income, focus on high-interest debt first. List all debts, make minimum payments on all, then pay extra on the highest rate debt. Would you like a specific repayment strategy?`;
      } else {
        return `I understand your question about finances. With ${income.toLocaleString()} ETB monthly income and ${input.household.household_size} household members, let's work together on your specific financial goals. Can you be more specific about what you'd like help with?`;
      }
    } else {
      return [
        `You make about ${income.toLocaleString()} ETB each month.`,
        `Rent and food take most of it — that's okay.`,
        `Try buying staples in bulk and reduce small phone costs.`,
        `You could aim to save about ${Math.floor(left * 0.1)} ETB this month.`,
        `Keep going step by step — you're doing great!`,
      ].join(" ");
    }
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
