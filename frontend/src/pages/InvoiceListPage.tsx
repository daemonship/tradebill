import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useInvoiceStore } from '../stores/invoiceStore';
import { useAuthStore } from '../stores/authStore';
import { InvoiceListItem, InvoiceStatus } from '../lib/api';
import { format } from '../lib/utils';

function StatusBadge({ status }: { status: InvoiceStatus }) {
  const colors = {
    draft: 'bg-gray-100 text-gray-700',
    sent: 'bg-blue-100 text-blue-700',
    paid: 'bg-green-100 text-green-700',
  };

  return (
    <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${colors[status]}`}>
      {status.charAt(0).toUpperCase() + status.slice(1)}
    </span>
  );
}

function InvoiceCard({ invoice, onMarkPaid }: { invoice: InvoiceListItem; onMarkPaid: (id: number) => void }) {
  const navigate = useNavigate();

  return (
    <div
      onClick={() => navigate(`/invoices/${invoice.id}`)}
      className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 cursor-pointer active:scale-[0.99] transition-transform"
    >
      <div className="flex justify-between items-start mb-2">
        <div>
          <h3 className="font-semibold text-gray-900">{invoice.client_name}</h3>
          <p className="text-sm text-gray-500 truncate max-w-[200px]">{invoice.job_address}</p>
        </div>
        <StatusBadge status={invoice.status} />
      </div>
      <div className="flex justify-between items-center">
        <div className="text-sm text-gray-500">
          {format.date(invoice.created_at)}
        </div>
        <div className="flex items-center gap-3">
          <span className="font-semibold text-gray-900">{format.currency(invoice.total)}</span>
          {invoice.status !== 'paid' && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                onMarkPaid(invoice.id);
              }}
              className="text-xs text-green-600 font-medium px-2 py-1 bg-green-50 rounded hover:bg-green-100"
            >
              Mark Paid
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

export default function InvoiceListPage() {
  const { invoices, fetchInvoices, updateStatus, isLoading, error } = useInvoiceStore();
  const { logout, profile } = useAuthStore();
  const navigate = useNavigate();
  const [showMenu, setShowMenu] = useState(false);

  useEffect(() => {
    fetchInvoices();
  }, [fetchInvoices]);

  const handleMarkPaid = async (id: number) => {
    try {
      await updateStatus(id, 'paid');
    } catch {
      // Error handled by store
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-lg mx-auto px-4 py-3 flex justify-between items-center">
          <div>
            <h1 className="text-lg font-bold text-gray-900">Invoices</h1>
            {profile && (
              <p className="text-xs text-gray-500">{profile.business_name}</p>
            )}
          </div>
          <div className="relative">
            <button
              onClick={() => setShowMenu(!showMenu)}
              className="p-2 text-gray-600 hover:bg-gray-100 rounded-full"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
            {showMenu && (
              <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-1">
                <button
                  onClick={() => {
                    setShowMenu(false);
                    navigate('/setup');
                  }}
                  className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                >
                  Edit Business Profile
                </button>
                <button
                  onClick={handleLogout}
                  className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-gray-100"
                >
                  Sign Out
                </button>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Content */}
      <main className="max-w-lg mx-auto px-4 py-4">
        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
            <p className="text-sm text-red-700">{error}</p>
          </div>
        )}

        {isLoading && invoices.length === 0 ? (
          <div className="text-center py-8">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-blue-600 border-t-transparent" />
          </div>
        ) : invoices.length === 0 ? (
          <div className="text-center py-12">
            <div className="w-16 h-16 bg-gray-200 rounded-full mx-auto mb-4 flex items-center justify-center">
              <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <h2 className="text-lg font-medium text-gray-900 mb-1">No invoices yet</h2>
            <p className="text-sm text-gray-500 mb-4">Create your first invoice to get started</p>
            <button
              onClick={() => navigate('/invoices/new')}
              className="inline-flex items-center px-4 py-2 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700"
            >
              Create Invoice
            </button>
          </div>
        ) : (
          <div className="space-y-3">
            {invoices.map((invoice) => (
              <InvoiceCard
                key={invoice.id}
                invoice={invoice}
                onMarkPaid={handleMarkPaid}
              />
            ))}
          </div>
        )}
      </main>

      {/* Floating Action Button */}
      <button
        onClick={() => navigate('/invoices/new')}
        className="fixed bottom-6 right-6 w-14 h-14 bg-blue-600 text-white rounded-full shadow-lg flex items-center justify-center hover:bg-blue-700 active:scale-95 transition-all"
        aria-label="Create new invoice"
      >
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
        </svg>
      </button>
    </div>
  );
}
