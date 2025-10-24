import { useEffect, useState } from "react";

const API = import.meta.env.VITE_API_BASE_URL as string;

export default function BudgetCoach() {
  const [advice, setAdvice] = useState<string>("");
  const [error, setError] = useState<string>("");

  useEffect(() => {
    // Demo household id 1 from seed
    fetch(`${API}/api/ai/budget/1`).then(async (r) => {
      if (!r.ok) throw new Error("Failed to fetch advice");
      const data = await r.json();
      setAdvice(data.advice);
    }).catch((e) => setError(e.message));
  }, []);

  return (
    <div className="max-w-xl mx-auto">
      <h1 className="text-2xl font-semibold mb-4">My Budget Coach</h1>
      {error && <div className="text-red-600">{error}</div>}
      <p className="whitespace-pre-line leading-7">{advice || "Loading advice..."}</p>
    </div>
  );
}
