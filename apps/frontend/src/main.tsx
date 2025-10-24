import React from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, Routes, Route, Link, useLocation } from "react-router-dom";
import Home from "./pages/Home";
import BudgetCoach from "./pages/BudgetCoach";
import Funding from "./pages/Funding";
import Microloan from "./pages/Microloan";
import WealthMap from "./pages/WealthMap";
import "./styles.css";

const Navigation = () => {
  const location = useLocation();
  
  const navItems = [
    { path: "/", label: "Home", icon: "🏠" },
    { path: "/coach", label: "Budget Coach", icon: "💰" },
    { path: "/funding", label: "Funding", icon: "🚀" },
    { path: "/loans", label: "Microloans", icon: "📈" },
    { path: "/wealth-map", label: "Wealth Map", icon: "🗺️" }
  ];

  return (
    <nav className="bg-gradient-to-r from-blue-600 to-purple-700 shadow-lg">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <Link to="/" className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-white rounded-lg flex items-center justify-center">
              <span className="text-blue-600 font-bold text-lg">F</span>
            </div>
            <span className="text-white font-bold text-xl">FinanceFlow</span>
          </Link>
          
          <div className="hidden md:flex space-x-1">
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 flex items-center space-x-2 ${
                  location.pathname === item.path
                    ? "bg-white/20 text-white"
                    : "text-white/80 hover:bg-white/10 hover:text-white"
                }`}
              >
                <span>{item.icon}</span>
                <span>{item.label}</span>
              </Link>
            ))}
          </div>
          
          <button className="bg-white text-blue-600 px-4 py-2 rounded-lg font-medium hover:bg-blue-50 transition-colors">
            Get Started
          </button>
        </div>
      </div>
    </nav>
  );
};

const App = () => (
  <BrowserRouter>
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      <Navigation />
      <main>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/coach" element={<BudgetCoach />} />
          <Route path="/funding" element={<Funding />} />
          <Route path="/loans" element={<Microloan />} />
          <Route path="/wealth-map" element={<WealthMap />} />
        </Routes>
      </main>
    </div>
  </BrowserRouter>
);

createRoot(document.getElementById("root")!).render(<App />);
