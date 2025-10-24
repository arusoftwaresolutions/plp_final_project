import React, { useState } from "react";

export default function Funding() {
  const [activeCategory, setActiveCategory] = useState("business");

  const categories = [
    { id: "business", label: "Business Growth", icon: "🚀" },
    { id: "education", label: "Education", icon: "🎓" },
    { id: "housing", label: "Housing", icon: "🏠" },
    { id: "emergency", label: "Emergency Fund", icon: "⚡" }
  ];

  const opportunities = {
    business: [
      {
        title: "Small Business Accelerator Grant",
        amount: "$5,000 - $25,000",
        deadline: "15 days left",
        description: "Non-repayable grants for innovative small businesses with growth potential",
        tags: ["Grant", "No Repayment", "Fast Approval"]
      },
      {
        title: "Community Impact Fund",
        amount: "$1,000 - $10,000", 
        deadline: "22 days left",
        description: "Funding for businesses that create positive community impact",
        tags: ["Social Impact", "Flexible Terms", "Community"]
      }
    ],
    education: [
      {
        title: "Skills Development Scholarship",
        amount: "$500 - $3,000",
        deadline: "8 days left", 
        description: "Support for professional development and certification programs",
        tags: ["Scholarship", "Career Growth", "No Interest"]
      }
    ],
    housing: [
      {
        title: "First-Time Homebuyer Assistance",
        amount: "$2,000 - $15,000",
        deadline: "30 days left",
        description: "Down payment assistance and closing cost support",
        tags: ["Government", "Low Interest", "Housing"]
      }
    ],
    emergency: [
      {
        title: "Emergency Relief Fund",
        amount: "$100 - $2,000", 
        deadline: "Available Now",
        description: "Quick access to emergency funds for unexpected expenses",
        tags: ["Emergency", "24hr Approval", "Crisis Support"]
      }
    ]
  };

  return (
    <div className="min-h-screen py-12">
      <div className="max-w-7xl mx-auto px-4">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
            Access <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600">Growth Capital</span>
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
            Discover vetted funding opportunities, grants, and investment options tailored to your financial goals and situation.
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid md:grid-cols-3 gap-6 mb-12">
          <div className="bg-gradient-to-r from-blue-500 to-blue-600 p-6 rounded-2xl text-white">
            <div className="text-3xl font-bold mb-2">$2.5M+</div>
            <div className="text-blue-100">Total Funds Accessed</div>
          </div>
          <div className="bg-gradient-to-r from-purple-500 to-purple-600 p-6 rounded-2xl text-white">
            <div className="text-3xl font-bold mb-2">85%</div>
            <div className="text-purple-100">Approval Rate</div>
          </div>
          <div className="bg-gradient-to-r from-green-500 to-green-600 p-6 rounded-2xl text-white">
            <div className="text-3xl font-bold mb-2">48hrs</div>
            <div className="text-green-100">Average Response</div>
          </div>
        </div>

        {/* Category Tabs */}
        <div className="mb-8">
          <div className="flex flex-wrap gap-2 justify-center">
            {categories.map((category) => (
              <button
                key={category.id}
                onClick={() => setActiveCategory(category.id)}
                className={`flex items-center space-x-2 px-6 py-3 rounded-xl font-medium transition-all duration-200 ${
                  activeCategory === category.id
                    ? "bg-blue-600 text-white shadow-lg"
                    : "bg-white text-gray-700 hover:bg-blue-50 border border-gray-200"
                }`}
              >
                <span>{category.icon}</span>
                <span>{category.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Funding Opportunities */}
        <div className="grid md:grid-cols-2 gap-8">
          {opportunities[activeCategory as keyof typeof opportunities]?.map((opportunity, index) => (
            <div key={index} className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden hover:shadow-xl transition-all duration-300">
              <div className="p-6">
                <div className="flex justify-between items-start mb-4">
                  <h3 className="text-xl font-semibold text-gray-900">{opportunity.title}</h3>
                  <span className="text-sm text-orange-600 font-medium bg-orange-50 px-3 py-1 rounded-full">
                    {opportunity.deadline}
                  </span>
                </div>
                
                <div className="text-2xl font-bold text-blue-600 mb-3">{opportunity.amount}</div>
                
                <p className="text-gray-600 mb-4 leading-relaxed">{opportunity.description}</p>
                
                <div className="flex flex-wrap gap-2 mb-6">
                  {opportunity.tags.map((tag, tagIndex) => (
                    <span key={tagIndex} className="text-xs font-medium bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
                      {tag}
                    </span>
                  ))}
                </div>
                
                <button className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 rounded-xl font-semibold hover:shadow-lg transform hover:-translate-y-1 transition-all duration-200">
                  Apply Now
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* Bottom CTA */}
        <div className="mt-16 text-center bg-gradient-to-r from-blue-50 to-purple-50 p-12 rounded-3xl">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Need Personalized Funding Advice?
          </h2>
          <p className="text-lg text-gray-600 mb-8 max-w-2xl mx-auto">
            Our funding specialists can help you identify the best opportunities based on your unique situation and goals.
          </p>
          <button className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-8 py-4 rounded-xl font-semibold text-lg hover:shadow-lg transform hover:scale-105 transition-all duration-200">
            Get Expert Guidance
          </button>
        </div>
      </div>
    </div>
  );
}