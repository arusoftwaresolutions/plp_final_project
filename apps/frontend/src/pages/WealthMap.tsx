import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

// Fix leaflet default markers
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjUiIGhlaWdodD0iNDEiIHZpZXdCb3g9IjAgMCAyNSA0MSIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEyLjUgMEMxOS40MDM2IDAgMjUgNS41OTY0NCAyNSAxMi41QzI1IDE5LjQwMzYgMTkuNDAzNiAyNSAxMi41IDI1QzUuNTk2NDQgMjUgMCAxOS40MDM2IDAgMTIuNUMwIDUuNTk2NDQgNS41OTY0NCAwIDEyLjUgMFoiIGZpbGw9IiMxMEI5ODEiLz4KPGNpcmNsZSBjeD0iMTIuNSIgY3k9IjEyLjUiIHI9IjMiIGZpbGw9IndoaXRlIi8+CjxwYXRoIGQ9Ik0xMi41IDI1TDEyLjUgNDEiIHN0cm9rZT0iIzEwQjk4MSIgc3Ryb2tlLXdpZHRoPSIyIi8+Cjwvc3ZnPgo=',
  iconUrl: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjUiIGhlaWdodD0iNDEiIHZpZXdCb3g9IjAgMCAyNSA0MSIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEyLjUgMEMxOS40MDM2IDAgMjUgNS41OTY0NCAyNSAxMi41QzI1IDE5LjQwMzYgMTkuNDAzNiAyNSAxMi41IDI1QzUuNTk2NDQgMjUgMCAxOS40MDM2IDAgMTIuNUMwIDUuNTk2NDQgNS41OTY0NCAwIDEyLjUgMFoiIGZpbGw9IiMxMEI5ODEiLz4KPGNpcmNsZSBjeD0iMTIuNSIgY3k9IjEyLjUiIHI9IjMiIGZpbGw9IndoaXRlIi8+CjxwYXRoIGQ9Ik0xMi41IDI1TDEyLjUgNDEiIHN0cm9rZT0iIzEwQjk4MSIgc3Ryb2tlLXdpZHRoPSIyIi8+Cjwvc3ZnPgo=',
  shadowUrl: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDEiIGhlaWdodD0iNDEiIHZpZXdCb3g9IjAgMCA0MSA0MSIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGVsbGlwc2UgY3g9IjIwLjUiIGN5PSIyMC41IiByeD0iMjAuNSIgcnk9IjIwLjUiIGZpbGw9ImJsYWNrIiBmaWxsLW9wYWNpdHk9IjAuMyIvPgo8L3N2Zz4K',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

export default function WealthMap() {
  const [selectedMetric, setSelectedMetric] = useState("opportunities");

  const metrics = [
    { id: "opportunities", label: "Growth Opportunities", icon: "🚀", color: "blue" },
    { id: "success", label: "Success Stories", icon: "💎", color: "purple" }, 
    { id: "funding", label: "Available Funding", icon: "💰", color: "green" },
    { id: "education", label: "Financial Education", icon: "📚", color: "orange" }
  ];

  const regions = [
    {
      name: "Downtown Business District",
      position: [9.03, 38.74] as [number, number],
      opportunities: 45,
      successRate: "89%",
      funding: "$2.5M",
      description: "High-growth entrepreneurship zone with excellent funding access"
    },
    {
      name: "Innovation Quarter", 
      position: [9.01, 38.76] as [number, number],
      opportunities: 32,
      successRate: "76%", 
      funding: "$1.8M",
      description: "Tech and innovation hub with startup accelerators"
    },
    {
      name: "Community Development Zone",
      position: [9.05, 38.72] as [number, number], 
      opportunities: 28,
      successRate: "82%",
      funding: "$1.2M",
      description: "Community-focused businesses with social impact funding"
    }
  ];

  const insights = [
    {
      title: "Rising Entrepreneurship",
      value: "+34%",
      description: "New business registrations this quarter",
      trend: "up"
    },
    {
      title: "Success Rate Growth", 
      value: "+12%",
      description: "Improvement in funding approval rates",
      trend: "up"
    },
    {
      title: "Community Impact",
      value: "50K+",
      description: "People reached through success stories",
      trend: "stable"
    },
    {
      title: "Available Capital",
      value: "$8.2M",
      description: "Total funding opportunities this month", 
      trend: "up"
    }
  ];

  return (
    <div className="min-h-screen py-12">
      <div className="max-w-7xl mx-auto px-4">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600">Wealth Creation</span> Opportunities
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
            Discover economic opportunities, success stories, and growth potential in your area and beyond.
          </p>
        </div>

        {/* Insights Cards */}
        <div className="grid md:grid-cols-4 gap-6 mb-8">
          {insights.map((insight, index) => (
            <div key={index} className="bg-white p-6 rounded-2xl shadow-lg border border-gray-100">
              <div className="flex items-center justify-between mb-3">
                <div className="text-2xl font-bold text-gray-900">{insight.value}</div>
                <div className={`w-3 h-3 rounded-full ${
                  insight.trend === "up" ? "bg-green-500" : "bg-blue-500"
                }`}></div>
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">{insight.title}</h3>
              <p className="text-sm text-gray-600">{insight.description}</p>
            </div>
          ))}
        </div>

        {/* Metric Selector */}
        <div className="mb-8">
          <div className="flex flex-wrap gap-2 justify-center">
            {metrics.map((metric) => (
              <button
                key={metric.id}
                onClick={() => setSelectedMetric(metric.id)}
                className={`flex items-center space-x-2 px-6 py-3 rounded-xl font-medium transition-all duration-200 ${
                  selectedMetric === metric.id
                    ? "bg-blue-600 text-white shadow-lg"
                    : "bg-white text-gray-700 hover:bg-blue-50 border border-gray-200"
                }`}
              >
                <span>{metric.icon}</span>
                <span>{metric.label}</span>
              </button>
            ))}
          </div>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Map */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
              <div className="p-4 border-b border-gray-100">
                <h2 className="text-xl font-semibold text-gray-900">Regional Opportunity Map</h2>
                <p className="text-gray-600">Click markers to explore opportunities in each area</p>
              </div>
              <div className="h-96">
                <MapContainer 
                  center={[9.03, 38.74]} 
                  zoom={12} 
                  style={{ height: "100%", width: "100%" }}
                  className="rounded-b-2xl"
                >
                  <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
                  {regions.map((region, index) => (
                    <Marker key={index} position={region.position}>
                      <Popup className="custom-popup">
                        <div className="p-2">
                          <h3 className="font-semibold text-gray-900 mb-2">{region.name}</h3>
                          <div className="space-y-1 text-sm">
                            <div className="flex justify-between">
                              <span>Opportunities:</span>
                              <span className="font-medium text-blue-600">{region.opportunities}</span>
                            </div>
                            <div className="flex justify-between">
                              <span>Success Rate:</span>
                              <span className="font-medium text-green-600">{region.successRate}</span>
                            </div>
                            <div className="flex justify-between">
                              <span>Available Funding:</span>
                              <span className="font-medium text-purple-600">{region.funding}</span>
                            </div>
                          </div>
                          <p className="text-xs text-gray-600 mt-2">{region.description}</p>
                        </div>
                      </Popup>
                    </Marker>
                  ))}
                </MapContainer>
              </div>
            </div>
          </div>

          {/* Regional Details */}
          <div className="space-y-6">
            <div className="bg-white rounded-2xl shadow-lg p-6">
              <h3 className="text-xl font-semibold text-gray-900 mb-4">Top Opportunity Zones</h3>
              <div className="space-y-4">
                {regions.map((region, index) => (
                  <div key={index} className="border border-gray-100 rounded-xl p-4 hover:shadow-md transition-shadow">
                    <h4 className="font-semibold text-gray-900 mb-2">{region.name}</h4>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <div className="text-gray-600">Opportunities</div>
                        <div className="font-semibold text-blue-600">{region.opportunities}</div>
                      </div>
                      <div>
                        <div className="text-gray-600">Success Rate</div>
                        <div className="font-semibold text-green-600">{region.successRate}</div>
                      </div>
                    </div>
                    <div className="mt-3">
                      <div className="text-gray-600 text-sm">Available Funding</div>
                      <div className="font-semibold text-purple-600">{region.funding}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-2xl p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">🎯 Personalized Opportunities</h3>
              <p className="text-gray-600 mb-4">
                Get tailored recommendations based on your location, skills, and financial goals.
              </p>
              <Link
                to="/opportunities"
                className="block w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 rounded-xl font-semibold hover:shadow-lg transform hover:-translate-y-1 transition-all duration-200 text-center"
              >
                Find My Opportunities
              </Link>
            </div>
          </div>
        </div>

        {/* Success Stories */}
        <div className="mt-16 bg-white rounded-3xl p-8 shadow-lg">
          <div className="flex items-center justify-between mb-8">
            <h2 className="text-3xl font-bold text-gray-900">Success Stories</h2>
            <Link
              to="/success-stories"
              className="bg-emerald-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-emerald-700 transition-colors"
            >
              View All Stories
            </Link>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">👩‍💼</span>
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Sarah's Tech Startup</h3>
              <p className="text-gray-600 text-sm">Secured $50K in funding and now employs 12 people</p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">👨‍🍳</span>
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Ahmed's Restaurant</h3>
              <p className="text-gray-600 text-sm">Expanded to 3 locations with microloan support</p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">👩‍🏫</span>
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Maria's Education Center</h3>
              <p className="text-gray-600 text-sm">Built community learning hub serving 500+ students</p>
            </div>
          </div>
        </div>

        {/* Financial Education CTA */}
        <div className="mt-8 bg-gradient-to-r from-teal-50 to-emerald-50 rounded-3xl p-8">
          <div className="text-center">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">📚 Build Your Financial Knowledge</h2>
            <p className="text-gray-600 text-lg mb-6 max-w-2xl mx-auto">
              Access comprehensive financial education resources designed to help you make informed decisions and grow your wealth.
            </p>
            <div className="flex flex-wrap gap-4 justify-center">
              <Link
                to="/education"
                className="bg-emerald-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-emerald-700 transition-colors"
              >
                Start Learning
              </Link>
              <Link
                to="/ai-chat"
                className="bg-teal-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-teal-700 transition-colors"
              >
                Ask AI Questions
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
