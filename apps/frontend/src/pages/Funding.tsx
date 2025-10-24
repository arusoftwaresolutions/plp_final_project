import React, { useState } from "react";
import { Link } from "react-router-dom";

export default function Funding() {
  const [activeCategory, setActiveCategory] = useState("business");
  const [showApplicationModal, setShowApplicationModal] = useState(false);
  const [selectedOpportunity, setSelectedOpportunity] = useState<any>(null);
  const [applicationData, setApplicationData] = useState({
    fullName: "",
    email: "",
    phone: "",
    monthlyIncome: "",
    householdSize: "",
    requestedAmount: "",
    businessDescription: "",
    fundingPurpose: "",
    experienceYears: ""
  });

  const handleApplyClick = (opportunity: any) => {
    setSelectedOpportunity(opportunity);
    setShowApplicationModal(true);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setApplicationData({
      ...applicationData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmitApplication = (e: React.FormEvent) => {
    e.preventDefault();
    // TODO: Submit to backend
    console.log("Application submitted:", { opportunity: selectedOpportunity, data: applicationData });
    alert("Application submitted successfully! We'll review it within 2-3 business days.");
    setShowApplicationModal(false);
    setApplicationData({
      fullName: "",
      email: "",
      phone: "",
      monthlyIncome: "",
      householdSize: "",
      requestedAmount: "",
      businessDescription: "",
      fundingPurpose: "",
      experienceYears: ""
    });
  };

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
            Access <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-600 to-teal-600">Growth Capital</span>
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
            Discover vetted funding opportunities, grants, and investment options tailored to your financial goals and situation.
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid md:grid-cols-3 gap-6 mb-12">
          <div className="bg-gradient-to-r from-emerald-500 to-emerald-600 p-6 rounded-2xl text-white">
            <div className="text-3xl font-bold mb-2">$2.5M+</div>
            <div className="text-emerald-100">Total Funds Accessed</div>
          </div>
          <div className="bg-gradient-to-r from-teal-500 to-teal-600 p-6 rounded-2xl text-white">
            <div className="text-3xl font-bold mb-2">85%</div>
            <div className="text-teal-100">Approval Rate</div>
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
                    ? "bg-emerald-600 text-white shadow-lg"
                    : "bg-white text-gray-700 hover:bg-emerald-50 border border-gray-200"
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
                
                <button 
                  onClick={() => handleApplyClick(opportunity)}
                  className="w-full bg-gradient-to-r from-emerald-600 to-teal-600 text-white py-3 rounded-xl font-semibold hover:shadow-lg transform hover:-translate-y-1 transition-all duration-200"
                >
                  Apply Now
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* Bottom CTA */}
        <div className="mt-16 text-center bg-gradient-to-r from-emerald-50 to-teal-50 p-12 rounded-3xl">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Need Personalized Funding Advice?
          </h2>
          <p className="text-lg text-gray-600 mb-8 max-w-2xl mx-auto">
            Our funding specialists can help you identify the best opportunities based on your unique situation and goals.
          </p>
          <Link 
            to="/ai-chat"
            className="inline-block bg-gradient-to-r from-emerald-600 to-teal-600 text-white px-8 py-4 rounded-xl font-semibold text-lg hover:shadow-lg transform hover:scale-105 transition-all duration-200"
          >
            Get Expert Guidance
          </Link>
        </div>
      </div>

      {/* Application Modal */}
      {showApplicationModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200">
              <div className="flex justify-between items-center">
                <h2 className="text-2xl font-bold text-gray-900">
                  Apply for {selectedOpportunity?.title}
                </h2>
                <button 
                  onClick={() => setShowApplicationModal(false)}
                  className="text-gray-500 hover:text-gray-700 text-2xl"
                >
                  ×
                </button>
              </div>
            </div>

            <form onSubmit={handleSubmitApplication} className="p-6 space-y-4">
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Full Name *
                  </label>
                  <input
                    type="text"
                    name="fullName"
                    value={applicationData.fullName}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                    placeholder="Your full name"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Email Address *
                  </label>
                  <input
                    type="email"
                    name="email"
                    value={applicationData.email}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                    placeholder="your@email.com"
                    required
                  />
                </div>
              </div>

              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Phone Number
                  </label>
                  <input
                    type="tel"
                    name="phone"
                    value={applicationData.phone}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                    placeholder="(555) 123-4567"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Requested Amount *
                  </label>
                  <input
                    type="number"
                    name="requestedAmount"
                    value={applicationData.requestedAmount}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                    placeholder="$5,000"
                    required
                  />
                </div>
              </div>

              <div className="grid md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Monthly Income
                  </label>
                  <input
                    type="number"
                    name="monthlyIncome"
                    value={applicationData.monthlyIncome}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                    placeholder="$3,000"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Household Size
                  </label>
                  <input
                    type="number"
                    name="householdSize"
                    value={applicationData.householdSize}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                    placeholder="4"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Experience (Years)
                  </label>
                  <input
                    type="number"
                    name="experienceYears"
                    value={applicationData.experienceYears}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                    placeholder="2"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Business/Project Description *
                </label>
                <textarea
                  name="businessDescription"
                  value={applicationData.businessDescription}
                  onChange={handleInputChange}
                  rows={3}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                  placeholder="Describe your business or project..."
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  How will you use the funding? *
                </label>
                <textarea
                  name="fundingPurpose"
                  value={applicationData.fundingPurpose}
                  onChange={handleInputChange}
                  rows={3}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                  placeholder="Equipment, inventory, marketing, etc..."
                  required
                />
              </div>

              <div className="bg-emerald-50 p-4 rounded-lg">
                <h4 className="font-semibold text-emerald-800 mb-2">📋 Application Review Process</h4>
                <ul className="text-sm text-emerald-700 space-y-1">
                  <li>• Initial review: 24-48 hours</li>
                  <li>• Document verification: 2-3 business days</li>
                  <li>• Final decision: 5-7 business days</li>
                </ul>
              </div>

              <div className="flex space-x-4 pt-4">
                <button
                  type="button"
                  onClick={() => setShowApplicationModal(false)}
                  className="flex-1 px-6 py-3 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 px-6 py-3 bg-gradient-to-r from-emerald-600 to-teal-600 text-white rounded-lg font-semibold hover:shadow-lg transition-all duration-200"
                >
                  Submit Application
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}