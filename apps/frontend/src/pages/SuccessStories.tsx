import React from "react";
import { Link } from "react-router-dom";

export default function SuccessStories() {
  const stories = [
    {
      id: 1,
      name: "Sarah Getachew",
      business: "TechFlow Solutions",
      category: "Technology",
      fundingAmount: "$50,000",
      employees: 12,
      revenue: "$120K annually",
      story: "Started with a small web development service from home. With microloan funding, expanded to offer full-stack solutions and mobile app development. Now serving 50+ local businesses.",
      image: "👩‍💼",
      location: "Addis Ababa",
      timeline: "2 years",
      impact: "Created 12 jobs, trained 25 people in digital skills"
    },
    {
      id: 2,
      name: "Ahmed Hassan",
      business: "Golden Spoon Restaurant Chain",
      category: "Food & Hospitality",
      fundingAmount: "$35,000",
      employees: 28,
      revenue: "$180K annually",
      story: "From a single food cart to three restaurant locations. Used funding to purchase equipment, hire staff, and establish supply chains. Known for authentic Ethiopian cuisine.",
      image: "👨‍🍳",
      location: "Dire Dawa",
      timeline: "3 years",
      impact: "28 jobs created, sources from 15 local farmers"
    },
    {
      id: 3,
      name: "Maria Tadesse",
      business: "Future Leaders Education Center",
      category: "Education",
      fundingAmount: "$25,000",
      employees: 8,
      revenue: "$85K annually",
      story: "Established community learning center offering computer training, English classes, and vocational skills. Serves over 500 students annually with flexible scheduling.",
      image: "👩‍🏫",
      location: "Hawassa",
      timeline: "18 months",
      impact: "500+ students trained, 85% job placement rate"
    },
    {
      id: 4,
      name: "Dawit Worku",
      business: "EcoFarm Cooperative",
      category: "Agriculture",
      fundingAmount: "$40,000",
      employees: 15,
      revenue: "$95K annually",
      story: "Led formation of farmer cooperative using sustainable agriculture practices. Secured funding for greenhouse technology and organic certification.",
      image: "👨‍🌾",
      location: "Bahir Dar",
      timeline: "2.5 years",
      impact: "15 families supported, 40% higher crop yields"
    },
    {
      id: 5,
      name: "Hanan Abebe",
      business: "Craft & Heritage",
      category: "Handicrafts",
      fundingAmount: "$15,000",
      employees: 6,
      revenue: "$42K annually",
      story: "Traditional handicraft business expanded to online sales and export. Funding helped set up workshop, buy equipment, and train artisans in quality standards.",
      image: "👩‍🎨",
      location: "Lalibela",
      timeline: "1.5 years",
      impact: "Preserved traditional crafts, 6 artisan jobs created"
    },
    {
      id: 6,
      name: "Solomon Bekele",
      business: "Mobile Repair Hub",
      category: "Technology Services",
      fundingAmount: "$20,000",
      employees: 4,
      revenue: "$55K annually",
      story: "Started fixing phones from a small kiosk. Funding enabled expansion to computers and tablets, plus training in advanced electronics repair.",
      image: "👨‍🔧",
      location: "Mekelle",
      timeline: "1 year",
      impact: "4 technician jobs, serves 200+ customers monthly"
    }
  ];

  const categories = ["All", "Technology", "Food & Hospitality", "Education", "Agriculture", "Handicrafts", "Technology Services"];
  const [selectedCategory, setSelectedCategory] = React.useState("All");

  const filteredStories = selectedCategory === "All" 
    ? stories 
    : stories.filter(story => story.category === selectedCategory);

  return (
    <div className="min-h-screen py-12">
      <div className="max-w-7xl mx-auto px-4">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-600 to-teal-600">Success Stories</span>
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
            Real entrepreneurs who transformed their lives and communities through access to funding and support. 
            These stories show what's possible when opportunity meets determination.
          </p>
        </div>

        {/* Stats */}
        <div className="grid md:grid-cols-4 gap-6 mb-12">
          <div className="bg-white p-6 rounded-2xl shadow-lg text-center">
            <div className="text-3xl font-bold text-emerald-600 mb-2">73</div>
            <div className="text-gray-600">Success Stories</div>
          </div>
          <div className="bg-white p-6 rounded-2xl shadow-lg text-center">
            <div className="text-3xl font-bold text-teal-600 mb-2">$2.1M</div>
            <div className="text-gray-600">Total Funding Provided</div>
          </div>
          <div className="bg-white p-6 rounded-2xl shadow-lg text-center">
            <div className="text-3xl font-bold text-blue-600 mb-2">427</div>
            <div className="text-gray-600">Jobs Created</div>
          </div>
          <div className="bg-white p-6 rounded-2xl shadow-lg text-center">
            <div className="text-3xl font-bold text-purple-600 mb-2">15K+</div>
            <div className="text-gray-600">Lives Impacted</div>
          </div>
        </div>

        {/* Category Filter */}
        <div className="mb-8">
          <div className="flex flex-wrap gap-2 justify-center">
            {categories.map((category) => (
              <button
                key={category}
                onClick={() => setSelectedCategory(category)}
                className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 ${
                  selectedCategory === category
                    ? "bg-emerald-600 text-white shadow-lg"
                    : "bg-white text-gray-700 hover:bg-emerald-50 border border-gray-200"
                }`}
              >
                {category}
              </button>
            ))}
          </div>
        </div>

        {/* Stories Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {filteredStories.map((story) => (
            <div key={story.id} className="bg-white rounded-2xl shadow-lg overflow-hidden hover:shadow-xl transition-shadow duration-300">
              <div className="p-6">
                {/* Header */}
                <div className="flex items-center mb-4">
                  <div className="w-16 h-16 bg-emerald-100 rounded-full flex items-center justify-center text-2xl mr-4">
                    {story.image}
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-gray-900">{story.name}</h3>
                    <p className="text-emerald-600 font-medium">{story.business}</p>
                    <p className="text-sm text-gray-500">{story.location}</p>
                  </div>
                </div>

                {/* Category Badge */}
                <div className="mb-4">
                  <span className="bg-teal-100 text-teal-800 text-xs font-medium px-3 py-1 rounded-full">
                    {story.category}
                  </span>
                </div>

                {/* Story */}
                <p className="text-gray-600 mb-4 text-sm leading-relaxed">
                  {story.story}
                </p>

                {/* Metrics */}
                <div className="space-y-2 mb-4">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">Funding:</span>
                    <span className="font-medium text-emerald-600">{story.fundingAmount}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">Employees:</span>
                    <span className="font-medium">{story.employees}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">Revenue:</span>
                    <span className="font-medium text-teal-600">{story.revenue}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">Timeline:</span>
                    <span className="font-medium">{story.timeline}</span>
                  </div>
                </div>

                {/* Impact */}
                <div className="bg-emerald-50 p-3 rounded-lg">
                  <h4 className="font-semibold text-emerald-800 text-sm mb-1">Community Impact:</h4>
                  <p className="text-emerald-700 text-xs">{story.impact}</p>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* CTA Section */}
        <div className="mt-16 bg-gradient-to-r from-emerald-600 to-teal-600 rounded-2xl p-8 text-white text-center">
          <h2 className="text-3xl font-bold mb-4">Ready to Write Your Success Story?</h2>
          <p className="text-emerald-100 mb-6 max-w-2xl mx-auto">
            Join these inspiring entrepreneurs who turned their dreams into thriving businesses. 
            Start your journey with funding and support tailored to your needs.
          </p>
          <div className="flex flex-wrap gap-4 justify-center">
            <Link
              to="/funding"
              className="bg-white text-emerald-600 px-6 py-3 rounded-lg font-semibold hover:bg-emerald-50 transition-colors"
            >
              Apply for Funding
            </Link>
            <Link
              to="/ai-chat"
              className="bg-emerald-500 text-white px-6 py-3 rounded-lg font-semibold hover:bg-emerald-400 transition-colors"
            >
              Get AI Guidance
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}