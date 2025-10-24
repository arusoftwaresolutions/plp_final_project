import React from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import Onboarding from "./pages/Onboarding";
import BudgetCoach from "./pages/BudgetCoach";
import Crowdfunding from "./pages/Crowdfunding";
import Microloan from "./pages/Microloan";
import PovertyMap from "./pages/PovertyMap";
import "./styles.css";

const App = () => (
  <BrowserRouter>
    <nav className="p-4 bg-white shadow flex gap-4">
      <Link to="/">Onboarding</Link>
      <Link to="/coach">My Budget Coach</Link>
      <Link to="/crowdfunding">Crowdfunding</Link>
      <Link to="/microloan">Microloan</Link>
      <Link to="/map">Poverty Map</Link>
    </nav>
    <main className="p-4">
      <Routes>
        <Route path="/" element={<Onboarding />} />
        <Route path="/coach" element={<BudgetCoach />} />
        <Route path="/crowdfunding" element={<Crowdfunding />} />
        <Route path="/microloan" element={<Microloan />} />
        <Route path="/map" element={<PovertyMap />} />
      </Routes>
    </main>
  </BrowserRouter>
);

createRoot(document.getElementById("root")!).render(<App />);
