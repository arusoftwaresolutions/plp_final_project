import React from 'react';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  type: 'success' | 'error';
  title: string;
  message: string;
  showSpinner?: boolean;
}

export default function Modal({ isOpen, onClose, type, title, message, showSpinner }: ModalProps) {
  if (!isOpen) return null;

  const bgColor = type === 'success' ? 'bg-green-50' : 'bg-red-50';
  const borderColor = type === 'success' ? 'border-green-400' : 'border-red-400';
  const textColor = type === 'success' ? 'text-green-700' : 'text-red-700';
  const iconColor = type === 'success' ? 'text-green-500' : 'text-red-500';
  const buttonColor = type === 'success' ? 'bg-green-600 hover:bg-green-700' : 'bg-red-600 hover:bg-red-700';
  const icon = type === 'success' ? '✅' : '⚠️';

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full mx-4 animate-fadeIn">
        <div className={`${bgColor} ${borderColor} border-2 rounded-2xl p-6`}>
          <div className="text-center">
            <div className="text-4xl mb-4">{icon}</div>
            <h3 className={`text-xl font-bold ${textColor} mb-2`}>
              {title}
            </h3>
            <p className={`${textColor} mb-4`}>
              {message}
            </p>
            
            {showSpinner && (
              <div className="flex justify-center items-center mb-4">
                <div className={`animate-spin rounded-full h-6 w-6 border-b-2 ${type === 'success' ? 'border-green-600' : 'border-red-600'}`}></div>
                <span className={`ml-2 text-sm ${textColor}`}>Processing...</span>
              </div>
            )}
            
            {!showSpinner && (
              <button
                onClick={onClose}
                className={`${buttonColor} text-white px-6 py-2 rounded-lg font-semibold transition-colors`}
              >
                OK
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}