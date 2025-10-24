import React, { useState } from "react";
import { Link } from "react-router-dom";

export default function Microloan() {
  const [activeStep, setActiveStep] = useState(1);
  const [loanData, setLoanData] = useState({
    // Personal Info
    fullName: "",
    email: "",
    phone: "",
    monthlyIncome: "",
    loanAmount: "",
    loanPurpose: "",
    repaymentPeriod: "12"
  });

  const [eligibilityResult, setEligibilityResult] = useState<any>(null);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setLoanData({ ...loanData, [name]: value });
  };

  const checkEligibility = () => {
    const income = parseFloat(loanData.monthlyIncome);
    const loanAmount = parseFloat(loanData.loanAmount);
    const monthlyPayment = loanAmount / parseFloat(loanData.repaymentPeriod);
    const debtToIncomeRatio = (monthlyPayment / income) * 100;
    
    const eligible = income >= 1000 && loanAmount <= income * 10 && debtToIncomeRatio <= 30;
    const interestRate = eligible ? (income >= 3000 ? 8 : 12) : 0;
    
    setEligibilityResult({
      eligible,
      interestRate,
      monthlyPayment: monthlyPayment.toFixed(2),
      debtToIncomeRatio: debtToIncomeRatio.toFixed(1),
      totalRepayment: (loanAmount * (1 + interestRate/100 * parseFloat(loanData.repaymentPeriod)/12)).toFixed(2)
    });
  };

  const submitApplication = () => {
    console.log("Loan application submitted:", loanData);
    alert("Loan application submitted successfully! We'll review it within 24-48 hours.");
  };

  const loanTypes = [
    { amount: "$500 - $2,000", purpose: "Emergency", rate: "8-12%" },
    { amount: "$1,000 - $5,000", purpose: "Business", rate: "10-15%" },
    { amount: "$500 - $3,000", purpose: "Education", rate: "6-10%" }
  ];

  return (
    <div className="min-h-screen py-8">
      <div className="max-w-4xl mx-auto px-4">
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
            Micro<span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-600 to-teal-600">Loans</span> Made Simple
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Access small loans with competitive rates and flexible terms
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-6 mb-12">
          {loanTypes.map((loan, index) => (
            <div key={index} className="bg-white p-6 rounded-2xl shadow-lg border">
              <div className="text-2xl font-bold text-emerald-600 mb-2">{loan.amount}</div>
              <h3 className="font-semibold text-gray-900 mb-2">{loan.purpose}</h3>
              <div className="text-gray-600">Rate: {loan.rate}</div>
            </div>
          ))}
        </div>

        <div className="bg-white rounded-2xl shadow-lg p-8">
          {activeStep === 1 && (
            <div>
              <h2 className="text-2xl font-bold mb-6">Loan Application</h2>
              <div className="space-y-6">
                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Full Name *
                    </label>
                    <input
                      type="text"
                      name="fullName"
                      value={loanData.fullName}
                      onChange={handleInputChange}
                      className="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-emerald-500"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Email Address *
                    </label>
                    <input
                      type="email"
                      name="email"
                      value={loanData.email}
                      onChange={handleInputChange}
                      className="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-emerald-500"
                      required
                    />
                  </div>
                </div>
                
                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Monthly Income ($) *
                    </label>
                    <input
                      type="number"
                      name="monthlyIncome"
                      value={loanData.monthlyIncome}
                      onChange={handleInputChange}
                      className="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-emerald-500"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Loan Amount ($) *
                    </label>
                    <input
                      type="number"
                      name="loanAmount"
                      value={loanData.loanAmount}
                      onChange={handleInputChange}
                      className="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-emerald-500"
                      required
                    />
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Loan Purpose *
                  </label>
                  <select
                    name="loanPurpose"
                    value={loanData.loanPurpose}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-emerald-500"
                    required
                  >
                    <option value="">Select purpose</option>
                    <option value="emergency">Emergency Expenses</option>
                    <option value="business">Business</option>
                    <option value="education">Education</option>
                    <option value="other">Other</option>
                  </select>
                </div>
              </div>
              
              <div className="mt-8 flex justify-between">
                <div></div>
                <button
                  onClick={() => setActiveStep(2)}
                  disabled={!loanData.fullName || !loanData.email || !loanData.monthlyIncome || !loanData.loanAmount}
                  className="bg-emerald-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-emerald-700 disabled:opacity-50"
                >
                  Check Eligibility
                </button>
              </div>
            </div>
          )}

          {activeStep === 2 && (
            <div>
              <h2 className="text-2xl font-bold mb-6">Eligibility Check</h2>
              {!eligibilityResult ? (
                <div className="text-center py-12">
                  <button
                    onClick={checkEligibility}
                    className="bg-gradient-to-r from-emerald-600 to-teal-600 text-white px-8 py-4 rounded-xl font-semibold text-lg"
                  >
                    Check My Eligibility
                  </button>
                </div>
              ) : (
                <div>
                  {eligibilityResult.eligible ? (
                    <div className="bg-emerald-50 border border-emerald-200 p-6 rounded-xl mb-6">
                      <h3 className="text-xl font-semibold text-emerald-800 mb-4">✅ You're Eligible!</h3>
                      <div className="grid md:grid-cols-2 gap-6">
                        <div>
                          <h4 className="font-semibold text-emerald-700 mb-2">Loan Terms:</h4>
                          <ul className="text-emerald-700">
                            <li>• Amount: ${parseInt(loanData.loanAmount).toLocaleString()}</li>
                            <li>• Rate: {eligibilityResult.interestRate}% annually</li>
                            <li>• Monthly: ${eligibilityResult.monthlyPayment}</li>
                            <li>• Total: ${eligibilityResult.totalRepayment}</li>
                          </ul>
                        </div>
                        <div className="text-center">
                          <button
                            onClick={submitApplication}
                            className="bg-emerald-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-emerald-700"
                          >
                            Apply Now
                          </button>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="bg-red-50 border border-red-200 p-6 rounded-xl">
                      <h3 className="text-xl font-semibold text-red-800 mb-4">❌ Not Eligible</h3>
                      <p className="text-red-700 mb-4">Based on your information, we cannot approve this loan at this time.</p>
                      <Link to="/ai-chat" className="bg-red-600 text-white px-6 py-2 rounded-lg font-medium">
                        Get Financial Advice
                      </Link>
                    </div>
                  )}
                </div>
              )}
              
              <div className="mt-8">
                <button
                  onClick={() => setActiveStep(1)}
                  className="border border-gray-300 text-gray-700 px-6 py-2 rounded-lg font-medium hover:bg-gray-50"
                >
                  ← Back
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
