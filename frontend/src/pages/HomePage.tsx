import { Link, Navigate } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';

export default function HomePage() {
  const { token } = useAuthStore();

  // Redirect to invoices if already logged in
  if (token) {
    return <Navigate to="/invoices" replace />;
  }

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      {/* Hero Section */}
      <div className="flex-1 flex flex-col items-center justify-center p-4">
        <div className="w-full max-w-sm text-center">
          {/* Logo/Icon */}
          <div className="w-20 h-20 bg-blue-600 rounded-2xl mx-auto mb-6 flex items-center justify-center shadow-lg">
            <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>

          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Tradebill
          </h1>
          <p className="text-gray-600 mb-8">
            Professional invoices for tradespeople. Create and send invoices in under 2 minutes from your phone.
          </p>

          {/* Features */}
          <div className="space-y-3 mb-8 text-left">
            <div className="flex items-center gap-3 p-3 bg-white rounded-lg shadow-sm">
              <span className="text-xl">🚿</span>
              <span className="text-sm text-gray-700">Trade-specific templates</span>
            </div>
            <div className="flex items-center gap-3 p-3 bg-white rounded-lg shadow-sm">
              <span className="text-xl">⚡</span>
              <span className="text-sm text-gray-700">Parts & labor tracking</span>
            </div>
            <div className="flex items-center gap-3 p-3 bg-white rounded-lg shadow-sm">
              <span className="text-xl">📧</span>
              <span className="text-sm text-gray-700">Email PDFs directly to clients</span>
            </div>
          </div>

          {/* CTA Buttons */}
          <div className="space-y-3">
            <Link
              to="/register"
              className="block w-full py-3 px-4 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            >
              Get Started
            </Link>
            <Link
              to="/login"
              className="block w-full py-3 px-4 bg-white border border-gray-300 text-gray-700 font-medium rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
            >
              Sign In
            </Link>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="py-4 text-center text-sm text-gray-500">
        Built for plumbers, electricians & HVAC pros
      </footer>
    </div>
  );
}
