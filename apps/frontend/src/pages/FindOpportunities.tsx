import React from "react";
import { Link } from "react-router-dom";

export default function FindOpportunities() {
  const opportunities = [
    {
      id: 1,
      title: "Local Business Grant",
      sponsor: "City Development Fund",
      amount: "$5,000 - $25,000",
      deadline: "Nov 30, 2025",
      category: "Small Business",
      location: "Addis Ababa",
      eligibility: [
        "Registered business (6+ months)",
        "At least 1 employee",
        "Operating within city limits"
      ],
      description: "Grants for small businesses to expand operations, hire staff, and invest in equipment.",
      link: "/funding"
    },
    {
      id: 2,
      title: "Startup Accelerator Program",
      sponsor: "Innovation Hub",
      amount: "$10,000 seed + mentorship",
      deadline: "Dec 15, 2025",
      category: "Technology",
      location: "Virtual",
      eligibility: [
        "MVP or prototype",
        "Founding team of 2+",
        "High-growth potential"
      ],
      description: "13-week accelerator with seed funding, mentorship, and investor demo day.",
      link: "/funding"
    },
    {
      id: 3,
      title: "Youth Entrepreneurship Microloan",
      sponsor: "Community Bank",
      amount: "$1,000 - $10,000",
      deadline: "Rolling",
      category: "Microloan",
      location: "Nationwide",
      eligibility: [
        "Age 18-30",
        "Business plan required",
        "Basic financial literacy course"
      ],
      description: "Low-interest microloans for young entrepreneurs starting or expanding small businesses.",
      link: "/loans"
    },
    {
      id: 4,
      title: "Women in Business Fund",
      sponsor: "Empower Foundation",
      amount: "$2,500 - $20,000",
      deadline: "Jan 10, 2026",
      category: "Women",
      location: "Nationwide",
      eligibility: [
        "Women-owned business (51%)",
        "Under 50 employees",
        "Impact on local community"
      ],
      description: "Funding and mentorship for women-owned businesses with growth potential.",
      link: "/funding"
    }
  ];

  const categories = ["All", "Small Business", "Technology", "Microloan", "Women"];
  const [selectedCategory, setSelectedCategory] = React.useState("All");

  const filtered = selectedCategory === "All" ? opportunities : opportunities.filter(o => o.category === selectedCategory);

  return (
    <div className="min-h-screen py-12">
      <div className="max-w-7xl mx-auto px-4">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600">Find Opportunities</span>
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
            Explore funding, programs, and resources available to support your business growth.
          </p>
        </div>

        {/* Filters */}
        <div className="mb-8">
          <div className="flex flex-wrap gap-2 justify-center">
            {categories.map((c) => (
              <button
                key={c}
                onClick={() => setSelectedCategory(c)}
                className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 ${selectedCategory === c ? 'bg-blue-600 text-white shadow-lg' : 'bg-white text-gray-700 hover:bg-blue-50 border border-gray-200'}`}
              >
                {c}
              </button>
            ))}
          </div>
        </div>

        {/* Opportunity List */}
        <div className="grid md:grid-cols-2 gap-6">
          {filtered.map((op) => (
            <div key={op.id} className="bg-white rounded-2xl shadow-lg p-6 hover:shadow-xl transition-shadow">
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="text-xl font-bold text-gray-900 mb-1">{op.title}</h3>
                  <div className="text-sm text-gray-600 mb-2">By {op.sponsor} • {op.location}</div>
                  <div className="flex flex-wrap gap-2 mb-3 text-sm">
                    <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full">{op.category}</span>
                    <span className="bg-emerald-100 text-emerald-800 px-3 py-1 rounded-full">{op.amount}</span>
                    <span className="bg-purple-100 text-purple-800 px-3 py-1 rounded-full">Deadline: {op.deadline}</span>
                  </div>
                </div>
                <Link to={op.link} className="bg-emerald-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-emerald-700 transition-colors">
                  Apply
                </Link>
              </div>
              <p className="text-gray-600 mt-3 mb-4">{op.description}</p>
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Eligibility:</h4>
                <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
                  {op.eligibility.map((e, i) => (<li key={i}>{e}</li>))}
                </ul>
              </div>
            </div>
          ))}
        </div>

        {/* CTA */}
        <div className="mt-16 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-8 text-white text-center">
          <h2 className="text-3xl font-bold mb-4">Need Help Choosing the Right Opportunity?</h2>
          <p className="text-blue-100 mb-6 max-w-2xl mx-auto">
            Chat with our AI advisor to find programs that match your goals and eligibility.
          </p>
          <Link to="/ai-chat" className="bg-white text-blue-600 px-6 py-3 rounded-lg font-semibold hover:bg-blue-50 transition-colors">
            Get AI Recommendations
          </Link>
        </div>
      </div>
    </div>
  );
}