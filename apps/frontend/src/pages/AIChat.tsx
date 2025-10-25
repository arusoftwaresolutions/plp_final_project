import React, { useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
interface Message {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: Date;
}

export default function AIChat() {
  const { user } = useAuth();
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      text: `Hello ${user?.name || ''}! I'm your personal financial advisor. I'm here to help you make smart financial decisions, create budgets, find savings opportunities, and plan for your future based on your specific situation. What would you like to discuss today?`,
      isUser: false,
      timestamp: new Date()
    }
  ]);
  const [inputText, setInputText] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const quickActions = [
    { text: "Help me create a budget", icon: "💰" },
    { text: "I need to save money", icon: "🏦" },
    { text: "Investment advice", icon: "📈" },
    { text: "Debt management", icon: "💳" },
    { text: "Emergency fund planning", icon: "🛡️" },
    { text: "Income optimization", icon: "💼" }
  ];

  const handleSendMessage = async () => {
    if (!inputText.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: inputText,
      isUser: true,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText("");
    setIsLoading(true);

    try {
      // Call the backend AI chat service with user's message and household context
      const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "https://poverty-alleviation.onrender.com";
      const householdId = user?.householdId || 1;
      const response = await fetch(`${API_BASE_URL}/api/ai/chat/${householdId}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          message: inputText
        })
      });

      if (response.ok) {
        const data = await response.json();
        const aiMessage: Message = {
          id: (Date.now() + 1).toString(),
          text: data.response || "I'm here to help with your financial questions. Can you tell me more about your specific situation?",
          isUser: false,
          timestamp: new Date()
        };
        setMessages(prev => [...prev, aiMessage]);
      } else {
        throw new Error("Failed to get AI response");
      }
    } catch (error) {
      console.error("Error getting AI response:", error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: "I'm having trouble connecting right now, but I'm here to help! Based on your question about budgeting, I recommend starting with the 50/30/20 rule: 50% for needs, 30% for wants, and 20% for savings and debt repayment. What's your current monthly income?",
        isUser: false,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuickAction = (text: string) => {
    setInputText(text);
  };

  return (
    <div className="min-h-screen py-6">
      <div className="max-w-4xl mx-auto px-4">
        {/* Header */}
        <div className="bg-white rounded-2xl shadow-lg mb-6 overflow-hidden">
          <div className="bg-gradient-to-r from-emerald-500 to-teal-600 p-6">
            <div className="flex items-center">
              <div className="w-12 h-12 bg-white rounded-full flex items-center justify-center mr-4">
                <span className="text-2xl">🤖</span>
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">AI Financial Advisor</h1>
                <p className="text-emerald-100">Get personalized financial guidance 24/7</p>
              </div>
            </div>
          </div>
          
          {/* Quick Actions */}
          <div className="p-6 border-b border-gray-100">
            <h3 className="text-sm font-medium text-gray-700 mb-3">Quick Topics:</h3>
            <div className="flex flex-wrap gap-2">
              {quickActions.map((action, index) => (
                <button
                  key={index}
                  onClick={() => handleQuickAction(action.text)}
                  className="flex items-center space-x-2 px-3 py-2 bg-emerald-50 text-emerald-700 rounded-lg text-sm hover:bg-emerald-100 transition-colors"
                >
                  <span>{action.icon}</span>
                  <span>{action.text}</span>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Chat Messages */}
        <div className="bg-white rounded-2xl shadow-lg mb-6">
          <div className="h-96 overflow-y-auto p-6 space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.isUser ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                    message.isUser
                      ? "bg-emerald-500 text-white"
                      : "bg-gray-100 text-gray-900"
                  }`}
                >
                  <p className="text-sm">{message.text}</p>
                  <p className={`text-xs mt-1 ${
                    message.isUser ? "text-emerald-100" : "text-gray-500"
                  }`}>
                    {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </p>
                </div>
              </div>
            ))}
            
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-gray-100 text-gray-900 px-4 py-2 rounded-lg max-w-xs">
                  <div className="flex space-x-2">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0.1s" }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0.2s" }}></div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Input Area */}
        <div className="bg-white rounded-2xl shadow-lg p-4">
          <div className="flex space-x-4">
            <input
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyPress={(e) => e.key === "Enter" && handleSendMessage()}
              className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
              placeholder="Ask me anything about your finances..."
              disabled={isLoading}
            />
            <button
              onClick={handleSendMessage}
              disabled={isLoading || !inputText.trim()}
              className="bg-gradient-to-r from-emerald-600 to-teal-600 text-white px-6 py-3 rounded-lg font-semibold hover:shadow-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Send
            </button>
          </div>
          
          <div className="mt-4 text-center">
            <p className="text-xs text-gray-500">
              💡 Tip: Be specific about your financial situation for better personalized advice
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}