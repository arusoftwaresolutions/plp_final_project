import React, { useState } from "react";
import { Link } from "react-router-dom";

export default function BudgetCoach() {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [income, setIncome] = useState(3000);
  const [expenses, setExpenses] = useState([
    { category: "Housing", amount: 1000, type: "fixed" },
    { category: "Food", amount: 400, type: "variable" },
    { category: "Transportation", amount: 300, type: "fixed" },
    { category: "Utilities", amount: 150, type: "fixed" },
    { category: "Entertainment", amount: 200, type: "variable" },
    { category: "Healthcare", amount: 100, type: "variable" }
  ]);
  const [savingsGoal, setSavingsGoal] = useState(500);
  const [newExpense, setNewExpense] = useState({ category: "", amount: "", type: "variable" });

  const totalExpenses = expenses.reduce((sum, expense) => sum + expense.amount, 0);
  const remainingBudget = income - totalExpenses;
  const savingsRate = ((remainingBudget / income) * 100).toFixed(1);

  const addExpense = () => {
    if (newExpense.category && newExpense.amount) {
      setExpenses([...expenses, {
        category: newExpense.category,
        amount: parseFloat(newExpense.amount),
        type: newExpense.type as "fixed" | "variable"
      }]);
      setNewExpense({ category: "", amount: "", type: "variable" });
    }
  };

  const deleteExpense = (index: number) => {
    setExpenses(expenses.filter((_, i) => i !== index));
  };

  const tabs = [
    { id: "dashboard", label: "Dashboard", icon: "📊" },
    { id: "budget", label: "Budget Tracker", icon: "💰" },
    { id: "savings", label: "Savings Goals", icon: "🎯" },
    { id: "insights", label: "AI Insights", icon: "🤖" }
  ];

  return (
    <div className="min-h-screen py-8">
      <div className="max-w-7xl mx-auto px-4">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Financial Dashboard</h1>
          <p className="text-xl text-gray-600">Take control of your financial future</p>
        </div>

        {/* Tabs */}
        <div className="mb-8">
          <div className="flex flex-wrap gap-2">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 px-6 py-3 rounded-xl font-medium transition-all duration-200 ${
                  activeTab === tab.id
                    ? "bg-emerald-600 text-white shadow-lg"
                    : "bg-white text-gray-700 hover:bg-emerald-50 border border-gray-200"
                }`}
              >
                <span>{tab.icon}</span>
                <span>{tab.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Dashboard Tab */}
        {activeTab === "dashboard" && (
          <div className="grid lg:grid-cols-3 gap-8">
            {/* Financial Summary */}
            <div className="lg:col-span-2 space-y-6">
              <div className="grid md:grid-cols-3 gap-6">
                <div className="bg-gradient-to-r from-emerald-500 to-emerald-600 p-6 rounded-2xl text-white">
                  <div className="text-3xl font-bold">${income.toLocaleString()}</div>
                  <div className="text-emerald-100">Monthly Income</div>
                </div>
                <div className="bg-gradient-to-r from-red-500 to-red-600 p-6 rounded-2xl text-white">
                  <div className="text-3xl font-bold">${totalExpenses.toLocaleString()}</div>
                  <div className="text-red-100">Total Expenses</div>
                </div>
                <div className={`bg-gradient-to-r p-6 rounded-2xl text-white ${
                  remainingBudget >= 0 ? "from-teal-500 to-teal-600" : "from-orange-500 to-orange-600"
                }`}>
                  <div className="text-3xl font-bold">${remainingBudget.toLocaleString()}</div>
                  <div className={remainingBudget >= 0 ? "text-teal-100" : "text-orange-100"}>
                    {remainingBudget >= 0 ? "Available" : "Over Budget"}
                  </div>
                </div>
              </div>

              {/* Expense Breakdown */}
              <div className="bg-white rounded-2xl shadow-lg p-6">
                <h3 className="text-xl font-semibold text-gray-900 mb-4">Expense Breakdown</h3>
                <div className="space-y-4">
                  {expenses.map((expense, index) => {
                    const percentage = ((expense.amount / totalExpenses) * 100).toFixed(1);
                    return (
                      <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                        <div className="flex items-center space-x-4">
                          <div className={`w-3 h-3 rounded-full ${
                            expense.type === "fixed" ? "bg-emerald-500" : "bg-teal-500"
                          }`}></div>
                          <div>
                            <div className="font-medium text-gray-900">{expense.category}</div>
                            <div className="text-sm text-gray-500">
                              {expense.type === "fixed" ? "Fixed" : "Variable"} • {percentage}%
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center space-x-3">
                          <span className="font-semibold text-gray-900">${expense.amount}</span>
                          <button
                            onClick={() => deleteExpense(index)}
                            className="text-red-500 hover:text-red-700"
                          >
                            ✕
                          </button>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>

            {/* Sidebar */}
            <div className="space-y-6">
              {/* Savings Rate */}
              <div className="bg-white rounded-2xl shadow-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Savings Rate</h3>
                <div className="text-center">
                  <div className={`text-4xl font-bold mb-2 ${
                    parseFloat(savingsRate) >= 20 ? "text-emerald-600" : 
                    parseFloat(savingsRate) >= 10 ? "text-yellow-600" : "text-red-600"
                  }`}>
                    {savingsRate}%
                  </div>
                  <p className="text-sm text-gray-600">
                    {parseFloat(savingsRate) >= 20 ? "Excellent!" :
                     parseFloat(savingsRate) >= 10 ? "Good progress" : "Needs improvement"}
                  </p>
                </div>
              </div>

              {/* Quick Actions */}
              <div className="bg-white rounded-2xl shadow-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
                <div className="space-y-3">
                  <button 
                    onClick={() => setActiveTab("budget")}
                    className="w-full bg-emerald-100 text-emerald-700 py-3 px-4 rounded-lg font-medium hover:bg-emerald-200 transition-colors"
                  >
                    📝 Update Budget
                  </button>
                  <button 
                    onClick={() => setActiveTab("savings")}
                    className="w-full bg-teal-100 text-teal-700 py-3 px-4 rounded-lg font-medium hover:bg-teal-200 transition-colors"
                  >
                    🎯 Set Savings Goal
                  </button>
                  <Link 
                    to="/ai-chat"
                    className="block w-full bg-blue-100 text-blue-700 py-3 px-4 rounded-lg font-medium hover:bg-blue-200 transition-colors text-center"
                  >
                    💬 Get AI Advice
                  </Link>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Budget Tab */}
        {activeTab === "budget" && (
          <div className="max-w-4xl mx-auto">
            <div className="bg-white rounded-2xl shadow-lg p-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Budget Management</h2>
              
              {/* Income Input */}
              <div className="mb-8">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Monthly Income
                </label>
                <input
                  type="number"
                  value={income}
                  onChange={(e) => setIncome(parseFloat(e.target.value) || 0)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                  placeholder="Enter your monthly income"
                />
              </div>

              {/* Add Expense */}
              <div className="mb-8 p-6 bg-gray-50 rounded-xl">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Add New Expense</h3>
                <div className="grid md:grid-cols-4 gap-4">
                  <input
                    type="text"
                    placeholder="Category (e.g., Groceries)"
                    value={newExpense.category}
                    onChange={(e) => setNewExpense({ ...newExpense, category: e.target.value })}
                    className="px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                  />
                  <input
                    type="number"
                    placeholder="Amount"
                    value={newExpense.amount}
                    onChange={(e) => setNewExpense({ ...newExpense, amount: e.target.value })}
                    className="px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                  />
                  <select
                    value={newExpense.type}
                    onChange={(e) => setNewExpense({ ...newExpense, type: e.target.value })}
                    className="px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                  >
                    <option value="variable">Variable</option>
                    <option value="fixed">Fixed</option>
                  </select>
                  <button
                    onClick={addExpense}
                    className="bg-emerald-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-emerald-700 transition-colors"
                  >
                    Add
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Other tabs */}
        {activeTab === "savings" && (
          <div className="max-w-4xl mx-auto">
            <div className="bg-white rounded-2xl shadow-lg p-8 text-center">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Savings Goals</h2>
              <p className="text-gray-600">Set and track your financial goals</p>
              <div className="mt-8">
                <Link 
                  to="/ai-chat" 
                  className="inline-block bg-emerald-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-emerald-700 transition-colors"
                >
                  Get Personalized Savings Advice
                </Link>
              </div>
            </div>
          </div>
        )}

        {activeTab === "insights" && (
          <div className="max-w-4xl mx-auto">
            <div className="bg-white rounded-2xl shadow-lg p-8 text-center">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">AI Financial Insights</h2>
              <p className="text-gray-600">Get personalized recommendations based on your spending patterns</p>
              <div className="mt-8">
                <Link 
                  to="/ai-chat" 
                  className="inline-block bg-emerald-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-emerald-700 transition-colors"
                >
                  Chat with AI Advisor
                </Link>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
