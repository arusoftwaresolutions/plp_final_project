import React from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, Routes, Route, Link, useLocation, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./contexts/AuthContext";
import Home from "./pages/Home";
import BudgetCoach from "./pages/BudgetCoach";
import Funding from "./pages/Funding";
import Microloan from "./pages/Microloan";
import WealthMap from "./pages/WealthMap";
import Auth from "./pages/Auth";
import AIChat from "./pages/AIChat";
import "./styles.css";

const Navigation = () => {
  const location = useLocation();
  const { isAuthenticated, user, logout } = useAuth();
  
  const publicNavItems = [
    { path: "/", label: "Home", icon: "🏠" }
  ];
  
  const privateNavItems = [
    { path: "/coach", label: "Dashboard", icon: "📊" },
    { path: "/funding", label: "Funding", icon: "🚀" },
    { path: "/loans", label: "Microloans", icon: "📈" },
    { path: "/wealth-map", label: "Wealth Map", icon: "🗺️" },
    { path: "/ai-chat", label: "AI Advisor", icon: "🤖" }
  ];

  const navItems = isAuthenticated ? privateNavItems : publicNavItems;

  return (
    <nav className="bg-gradient-to-r from-emerald-600 to-teal-700 shadow-lg">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <Link to="/" className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-white rounded-lg flex items-center justify-center">
              <span className="text-emerald-600 font-bold text-lg">$</span>
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
          
          <div className="flex items-center space-x-4">
            {isAuthenticated ? (
              <>
                <span className="text-white/80 text-sm">Welcome, {user?.name}</span>
                <button 
                  onClick={logout}
                  className="bg-white/20 text-white px-4 py-2 rounded-lg font-medium hover:bg-white/30 transition-colors"
                >
                  Logout
                </button>
              </>
            ) : (
              <Link to="/auth" className="bg-white text-emerald-600 px-4 py-2 rounded-lg font-medium hover:bg-emerald-50 transition-colors">
                Get Started
              </Link>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};

const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? <>{children}</> : <Navigate to="/auth" replace />;
};

const AppRoutes = () => {
  const { isAuthenticated } = useAuth();
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 to-teal-50">
      <Navigation />
      <main>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/auth" element={isAuthenticated ? <Navigate to="/coach" replace /> : <Auth />} />
          <Route path="/coach" element={<ProtectedRoute><BudgetCoach /></ProtectedRoute>} />
          <Route path="/funding" element={<ProtectedRoute><Funding /></ProtectedRoute>} />
          <Route path="/loans" element={<ProtectedRoute><Microloan /></ProtectedRoute>} />
          <Route path="/wealth-map" element={<ProtectedRoute><WealthMap /></ProtectedRoute>} />
          <Route path="/ai-chat" element={<ProtectedRoute><AIChat /></ProtectedRoute>} />
        </Routes>
      </main>
    </div>
  );
};

const App = () => (
  <BrowserRouter>
    <AuthProvider>
      <AppRoutes />
    </AuthProvider>
  </BrowserRouter>
);

createRoot(document.getElementById("root")!).render(<App />);
