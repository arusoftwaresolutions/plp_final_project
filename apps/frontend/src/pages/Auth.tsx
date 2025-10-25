import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import Modal from '../components/Modal';

export default function Auth() {
  const [isLogin, setIsLogin] = useState(true);
  const [loading, setLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [modalType, setModalType] = useState<'success' | 'error'>('success');
  const [modalTitle, setModalTitle] = useState('');
  const [modalMessage, setModalMessage] = useState('');
  const [showModalSpinner, setShowModalSpinner] = useState(false);
  const [showForm, setShowForm] = useState(true);
  const { login, register } = useAuth();
  const navigate = useNavigate();
  
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
    confirmPassword: "",
    monthlyIncome: "",
    householdSize: ""
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    // Close modal if it's open
    if (showModal) setShowModal(false);
  };

  const showErrorModal = (message: string) => {
    setModalType('error');
    setModalTitle('Error');
    setModalMessage(message);
    setShowModalSpinner(false);
    setShowModal(true);
  };

  const showSuccessModal = (message: string, withSpinner = false) => {
    setModalType('success');
    setModalTitle('Success!');
    setModalMessage(message);
    setShowModalSpinner(withSpinner);
    setShowModal(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      if (isLogin) {
        await login(formData.email, formData.password);
        showSuccessModal('Login successful! Redirecting to your dashboard...', true);
        setTimeout(() => {
          setShowModal(false);
          navigate('/coach');
        }, 2000);
      } else {
        if (formData.password !== formData.confirmPassword) {
          showErrorModal('Passwords do not match. Please check and try again.');
          setLoading(false);
          return;
        }
        
        await register(
          formData.name,
          formData.email,
          formData.password,
          parseInt(formData.monthlyIncome) || 0,
          parseInt(formData.householdSize) || 1
        );
        
        setShowForm(false);
        showSuccessModal('Welcome to FinanceFlow! Your account has been created successfully. Redirecting to your dashboard...', true);
        
        setTimeout(() => {
          setShowModal(false);
          navigate('/coach');
        }, 3000);
      }
    } catch (err) {
      console.error('Auth error:', err);
      let errorMessage = 'Authentication failed';
      
      if (err instanceof Error) {
        if (err.message.includes('fetch')) {
          errorMessage = 'Unable to connect to server. Please check your internet connection and try again.';
        } else if (err.message.includes('json') || err.message.includes('Unexpected end')) {
          errorMessage = 'Server is currently experiencing issues. Please try again in a moment.';
        } else {
          errorMessage = err.message;
        }
      }
      
      showErrorModal(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen py-12">
      <div className="max-w-md mx-auto px-4">
        <div className="bg-white rounded-2xl shadow-xl border border-gray-100 overflow-hidden">
          <div className="bg-gradient-to-r from-emerald-500 to-teal-600 p-8 text-center">
            <div className="w-16 h-16 bg-white rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-emerald-600 font-bold text-2xl">$</span>
            </div>
            <h1 className="text-2xl font-bold text-white mb-2">
              {isLogin ? "Welcome Back!" : "Start Your Journey"}
            </h1>
            <p className="text-emerald-100">
              {isLogin ? "Access your financial dashboard" : "Take control of your finances today"}
            </p>
          </div>

          <div className="p-8">
            <div className="flex mb-6">
              <button
                className={`flex-1 py-2 text-center font-medium rounded-lg mr-2 transition-colors ${
                  isLogin
                    ? "bg-emerald-100 text-emerald-700"
                    : "text-gray-500 hover:bg-gray-100"
                }`}
                onClick={() => setIsLogin(true)}
              >
                Login
              </button>
              <button
                className={`flex-1 py-2 text-center font-medium rounded-lg ml-2 transition-colors ${
                  !isLogin
                    ? "bg-emerald-100 text-emerald-700"
                    : "text-gray-500 hover:bg-gray-100"
                }`}
                onClick={() => setIsLogin(false)}
              >
                Sign Up
              </button>
            </div>

            
            {showForm ? (
              <form onSubmit={handleSubmit} className="space-y-4">
              {!isLogin && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Full Name
                  </label>
                  <input
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                    placeholder="Enter your full name"
                    required={!isLogin}
                  />
                </div>
              )}

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Email Address
                </label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                  placeholder="Enter your email"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Password
                </label>
                <input
                  type="password"
                  name="password"
                  value={formData.password}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                  placeholder="Enter your password"
                  required
                />
              </div>

              {!isLogin && (
                <>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Confirm Password
                    </label>
                    <input
                      type="password"
                      name="confirmPassword"
                      value={formData.confirmPassword}
                      onChange={handleInputChange}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                      placeholder="Confirm your password"
                      required={!isLogin}
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Monthly Income ($)
                      </label>
                      <input
                        type="number"
                        name="monthlyIncome"
                        value={formData.monthlyIncome}
                        onChange={handleInputChange}
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                        placeholder="3000"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Household Size
                      </label>
                      <input
                        type="number"
                        name="householdSize"
                        value={formData.householdSize}
                        onChange={handleInputChange}
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                        placeholder="4"
                      />
                    </div>
                  </div>
                </>
              )}

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-gradient-to-r from-emerald-600 to-teal-600 text-white py-3 rounded-lg font-semibold hover:shadow-lg transform hover:-translate-y-1 transition-all duration-200 disabled:opacity-50 disabled:transform-none disabled:hover:shadow-none"
              >
                {loading ? (
                  <div className="flex items-center justify-center">
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                    {isLogin ? "Signing In..." : "Creating Account..."}
                  </div>
                ) : (
                  isLogin ? "Sign In" : "Create Account"
                )}
              </button>
              </form>
            ) : (
              <div className="text-center py-8">
                <div className="text-6xl mb-4">🎉</div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  Welcome to FinanceFlow!
                </h3>
                <p className="text-gray-600 mb-4">
                  Your account has been created successfully. You'll be redirected to your personalized financial dashboard shortly.
                </p>
                <div className="flex justify-center">
                  <div className="animate-pulse bg-emerald-100 text-emerald-700 px-4 py-2 rounded-lg">
                    Preparing your dashboard...
                  </div>
                </div>
              </div>
            )}

            <div className="mt-6 text-center">
              <Link to="/" className="text-emerald-600 hover:text-emerald-700 font-medium">
                ← Back to Home
              </Link>
            </div>
          </div>
        </div>

        <div className="mt-8 text-center">
          <p className="text-gray-600 mb-4">🔒 Your financial data is encrypted and secure</p>
          <div className="flex justify-center space-x-6 text-sm text-gray-500">
            <span>✓ Bank-level security</span>
            <span>✓ Privacy protected</span>
            <span>✓ No data selling</span>
          </div>
        </div>
      </div>
      
      <Modal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        type={modalType}
        title={modalTitle}
        message={modalMessage}
        showSpinner={showModalSpinner}
      />
    </div>
  );
}