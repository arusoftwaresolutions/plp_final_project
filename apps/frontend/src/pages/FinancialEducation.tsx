import React, { useState } from "react";
import { Link } from "react-router-dom";

export default function FinancialEducation() {
  const [activeCategory, setActiveCategory] = useState("basics");

  const categories = [
    { id: "basics", label: "Financial Basics", icon: "📚", color: "emerald" },
    { id: "budgeting", label: "Budgeting", icon: "💰", color: "teal" },
    { id: "saving", label: "Saving & Investment", icon: "🏦", color: "blue" },
    { id: "business", label: "Business Finance", icon: "🚀", color: "purple" },
    { id: "credit", label: "Credit & Loans", icon: "💳", color: "orange" }
  ];

  const content = {
    basics: {
      title: "Financial Basics",
      description: "Build a strong foundation with essential financial concepts everyone should know.",
      lessons: [
        {
          title: "Understanding Money Flow",
          duration: "15 min",
          difficulty: "Beginner",
          description: "Learn how money moves in and out of your life and how to track it effectively.",
          topics: ["Income sources", "Types of expenses", "Cash flow basics", "Financial awareness"]
        },
        {
          title: "Setting Financial Goals",
          duration: "20 min", 
          difficulty: "Beginner",
          description: "Create SMART financial goals that motivate and guide your money decisions.",
          topics: ["SMART goals framework", "Short vs long-term goals", "Goal prioritization", "Success tracking"]
        },
        {
          title: "Building Emergency Funds",
          duration: "25 min",
          difficulty: "Beginner",
          description: "Why emergency funds matter and how to build yours step by step.",
          topics: ["Emergency fund importance", "How much to save", "Where to keep it", "Building strategies"]
        },
        {
          title: "Financial Planning Basics",
          duration: "30 min",
          difficulty: "Intermediate",
          description: "Create a comprehensive financial plan for your future.",
          topics: ["Financial assessment", "Planning timeline", "Risk management", "Plan review process"]
        }
      ]
    },
    budgeting: {
      title: "Budgeting Mastery",
      description: "Master the art of budgeting with practical tools and proven strategies.",
      lessons: [
        {
          title: "The 50/30/20 Rule",
          duration: "18 min",
          difficulty: "Beginner",
          description: "Simple budgeting framework: 50% needs, 30% wants, 20% savings and debt.",
          topics: ["Rule breakdown", "Identifying needs vs wants", "Implementation tips", "Adjustments"]
        },
        {
          title: "Zero-Based Budgeting",
          duration: "25 min",
          difficulty: "Intermediate", 
          description: "Give every ETB a purpose with this comprehensive budgeting method.",
          topics: ["Zero-based principles", "Monthly planning", "Expense categories", "Tracking systems"]
        },
        {
          title: "Budget Tracking Tools",
          duration: "20 min",
          difficulty: "Beginner",
          description: "Apps, spreadsheets, and tools to make budget tracking effortless.",
          topics: ["Mobile apps", "Spreadsheet templates", "Manual tracking", "Automation tips"]
        },
        {
          title: "Handling Budget Challenges",
          duration: "22 min",
          difficulty: "Intermediate",
          description: "Overcome common budgeting obstacles and stay on track.",
          topics: ["Irregular income", "Unexpected expenses", "Motivation strategies", "Budget adjustments"]
        }
      ]
    },
    saving: {
      title: "Saving & Investment",
      description: "Grow your wealth through smart saving strategies and investment basics.",
      lessons: [
        {
          title: "Saving Strategies That Work",
          duration: "20 min",
          difficulty: "Beginner",
          description: "Proven methods to save more money without feeling deprived.",
          topics: ["Pay yourself first", "Automatic savings", "The envelope method", "Micro-saving tips"]
        },
        {
          title: "Understanding Interest & Compound Growth",
          duration: "25 min",
          difficulty: "Beginner",
          description: "How your money can grow over time with compound interest.",
          topics: ["Simple vs compound interest", "Time value of money", "Growth calculations", "Practical examples"]
        },
        {
          title: "Investment Basics for Beginners",
          duration: "35 min",
          difficulty: "Intermediate",
          description: "Start your investment journey with fundamental concepts and options.",
          topics: ["Risk and return", "Investment types", "Diversification", "Getting started"]
        },
        {
          title: "Building Wealth Over Time",
          duration: "30 min",
          difficulty: "Intermediate",
          description: "Long-term wealth building strategies and financial independence.",
          topics: ["Wealth mindset", "Asset accumulation", "Income streams", "Retirement planning"]
        }
      ]
    },
    business: {
      title: "Business Finance",
      description: "Essential financial skills for entrepreneurs and business owners.",
      lessons: [
        {
          title: "Business Financial Planning",
          duration: "30 min",
          difficulty: "Intermediate",
          description: "Create financial projections and business plans that attract funding.",
          topics: ["Revenue forecasting", "Expense planning", "Cash flow projections", "Break-even analysis"]
        },
        {
          title: "Understanding Business Loans",
          duration: "25 min",
          difficulty: "Intermediate",
          description: "Navigate business loan options and improve your approval chances.",
          topics: ["Loan types", "Application process", "Documentation needed", "Approval strategies"]
        },
        {
          title: "Managing Business Cash Flow",
          duration: "28 min",
          difficulty: "Intermediate",
          description: "Keep your business financially healthy with proper cash flow management.",
          topics: ["Cash flow cycles", "Receivables management", "Payment terms", "Emergency planning"]
        },
        {
          title: "Business Growth Financing",
          duration: "32 min",
          difficulty: "Advanced",
          description: "Funding options for scaling your business to the next level.",
          topics: ["Growth financing", "Equity vs debt", "Investor readiness", "Scaling strategies"]
        }
      ]
    },
    credit: {
      title: "Credit & Loans",
      description: "Build good credit and make smart borrowing decisions.",
      lessons: [
        {
          title: "Understanding Credit Scores",
          duration: "22 min",
          difficulty: "Beginner",
          description: "What credit scores are, how they're calculated, and why they matter.",
          topics: ["Credit score basics", "Score calculation", "Credit reports", "Score improvement"]
        },
        {
          title: "Types of Credit and Loans",
          duration: "25 min",
          difficulty: "Beginner",
          description: "Navigate different credit products and choose the right ones for you.",
          topics: ["Credit cards", "Personal loans", "Microloans", "Secured vs unsecured"]
        },
        {
          title: "Loan Application Success",
          duration: "20 min",
          difficulty: "Intermediate",
          description: "Prepare strong loan applications and improve your approval odds.",
          topics: ["Application preparation", "Documentation", "Credit improvement", "Lender selection"]
        },
        {
          title: "Debt Management Strategies",
          duration: "30 min",
          difficulty: "Intermediate",
          description: "Pay off debt efficiently and avoid common debt traps.",
          topics: ["Debt avalanche", "Debt snowball", "Consolidation options", "Prevention strategies"]
        }
      ]
    }
  };

  const currentContent = content[activeCategory as keyof typeof content];

  return (
    <div className="min-h-screen py-12">
      <div className="max-w-7xl mx-auto px-4">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-600 to-teal-600">Financial Education</span>
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
            Empower yourself with financial knowledge. Our comprehensive courses are designed to help you build 
            wealth, make smart money decisions, and achieve financial freedom.
          </p>
        </div>

        {/* Stats */}
        <div className="grid md:grid-cols-4 gap-6 mb-12">
          <div className="bg-white p-6 rounded-2xl shadow-lg text-center">
            <div className="text-3xl font-bold text-emerald-600 mb-2">50+</div>
            <div className="text-gray-600">Course Modules</div>
          </div>
          <div className="bg-white p-6 rounded-2xl shadow-lg text-center">
            <div className="text-3xl font-bold text-teal-600 mb-2">2,400+</div>
            <div className="text-gray-600">Students Enrolled</div>
          </div>
          <div className="bg-white p-6 rounded-2xl shadow-lg text-center">
            <div className="text-3xl font-bold text-blue-600 mb-2">95%</div>
            <div className="text-gray-600">Completion Rate</div>
          </div>
          <div className="bg-white p-6 rounded-2xl shadow-lg text-center">
            <div className="text-3xl font-bold text-purple-600 mb-2">4.8/5</div>
            <div className="text-gray-600">Average Rating</div>
          </div>
        </div>

        {/* Category Navigation */}
        <div className="mb-8">
          <div className="flex flex-wrap gap-2 justify-center">
            {categories.map((category) => (
              <button
                key={category.id}
                onClick={() => setActiveCategory(category.id)}
                className={`flex items-center space-x-2 px-6 py-3 rounded-xl font-medium transition-all duration-200 ${
                  activeCategory === category.id
                    ? `bg-${category.color}-600 text-white shadow-lg`
                    : "bg-white text-gray-700 hover:bg-gray-50 border border-gray-200"
                }`}
              >
                <span>{category.icon}</span>
                <span>{category.label}</span>
              </button>
            ))}
          </div>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Course Content */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-2xl shadow-lg p-8">
              <div className="mb-8">
                <h2 className="text-3xl font-bold text-gray-900 mb-4">{currentContent.title}</h2>
                <p className="text-gray-600 text-lg">{currentContent.description}</p>
              </div>

              {/* Lessons */}
              <div className="space-y-6">
                {currentContent.lessons.map((lesson, index) => (
                  <div key={index} className="border border-gray-100 rounded-xl p-6 hover:shadow-md transition-shadow">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex-1">
                        <h3 className="text-xl font-semibold text-gray-900 mb-2">{lesson.title}</h3>
                        <p className="text-gray-600 mb-3">{lesson.description}</p>
                        <div className="flex flex-wrap gap-3 text-sm">
                          <span className="bg-emerald-100 text-emerald-800 px-3 py-1 rounded-full">
                            ⏱️ {lesson.duration}
                          </span>
                          <span className={`px-3 py-1 rounded-full ${
                            lesson.difficulty === 'Beginner' ? 'bg-green-100 text-green-800' :
                            lesson.difficulty === 'Intermediate' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-red-100 text-red-800'
                          }`}>
                            📊 {lesson.difficulty}
                          </span>
                        </div>
                      </div>
                      <button className="ml-4 bg-emerald-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-emerald-700 transition-colors whitespace-nowrap">
                        Start Lesson
                      </button>
                    </div>

                    {/* Topics Covered */}
                    <div className="mt-4">
                      <h4 className="font-medium text-gray-900 mb-2">Topics Covered:</h4>
                      <div className="flex flex-wrap gap-2">
                        {lesson.topics.map((topic, topicIndex) => (
                          <span key={topicIndex} className="bg-gray-100 text-gray-700 px-3 py-1 rounded-lg text-sm">
                            {topic}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Progress Card */}
            <div className="bg-white rounded-2xl shadow-lg p-6">
              <h3 className="text-xl font-semibold text-gray-900 mb-4">Your Progress</h3>
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between text-sm mb-2">
                    <span className="text-gray-600">Overall Progress</span>
                    <span className="font-medium">32%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div className="bg-emerald-600 h-2 rounded-full" style={{ width: '32%' }}></div>
                  </div>
                </div>
                <div className="text-sm text-gray-600">
                  <div>Completed: 8 lessons</div>
                  <div>Remaining: 17 lessons</div>
                </div>
              </div>
            </div>

            {/* Quick Start */}
            <div className="bg-gradient-to-r from-teal-50 to-emerald-50 rounded-2xl p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">🚀 Quick Start Guide</h3>
              <p className="text-gray-600 mb-4">
                New to financial education? Start with our recommended learning path.
              </p>
              <div className="space-y-2 text-sm">
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-emerald-600 rounded-full"></div>
                  <span>1. Financial Basics</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-teal-600 rounded-full"></div>
                  <span>2. Budgeting Mastery</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
                  <span>3. Saving & Investment</span>
                </div>
              </div>
              <button className="w-full mt-4 bg-emerald-600 text-white py-2 rounded-lg font-medium hover:bg-emerald-700 transition-colors">
                Start Learning Path
              </button>
            </div>

            {/* AI Support */}
            <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-2xl p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">🤖 AI Learning Assistant</h3>
              <p className="text-gray-600 mb-4">
                Get personalized help and clarification on any financial concept.
              </p>
              <Link
                to="/ai-chat"
                className="block w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-2 rounded-lg font-medium hover:shadow-lg transition-all text-center"
              >
                Chat with AI Tutor
              </Link>
            </div>

            {/* Certificate */}
            <div className="bg-gradient-to-r from-yellow-50 to-orange-50 rounded-2xl p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">🏆 Earn Certificate</h3>
              <p className="text-gray-600 mb-4">
                Complete course modules to earn verified certificates for your achievements.
              </p>
              <div className="text-sm text-gray-600">
                Next milestone: Complete 5 more lessons
              </div>
            </div>
          </div>
        </div>

        {/* CTA Section */}
        <div className="mt-16 bg-gradient-to-r from-emerald-600 to-teal-600 rounded-2xl p-8 text-white text-center">
          <h2 className="text-3xl font-bold mb-4">Ready to Transform Your Financial Future?</h2>
          <p className="text-emerald-100 mb-6 max-w-2xl mx-auto">
            Join thousands of learners who've improved their financial literacy and achieved their money goals. 
            Start your journey today.
          </p>
          <div className="flex flex-wrap gap-4 justify-center">
            <Link
              to="/coach"
              className="bg-white text-emerald-600 px-6 py-3 rounded-lg font-semibold hover:bg-emerald-50 transition-colors"
            >
              View Dashboard
            </Link>
            <Link
              to="/ai-chat"
              className="bg-emerald-500 text-white px-6 py-3 rounded-lg font-semibold hover:bg-emerald-400 transition-colors"
            >
              Get Personalized Guidance
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}