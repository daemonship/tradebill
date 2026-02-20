import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useInvoiceStore } from '../stores/invoiceStore';
import { format } from '../lib/utils';
import { InvoiceStatus } from '../lib/api';

export default function InvoiceDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const {
    currentInvoice,
    fetchInvoice,
    updateStatus,
    sendInvoice,
    isLoading,
    error,
    clearError,
    clearCurrentInvoice,
  } = useInvoiceStore();

  const [showActions, setShowActions] = useState(false);

  useEffect(() => {
    if (id) {
      fetchInvoice(parseInt(id, 10));
    }
    return () => {
      clearCurrentInvoice();
    };
  }, [id, fetchInvoice, clearCurrentInvoice]);

  const handleMarkPaid = async () => {
    if (!id) return;
    clearError();
    try {
      await updateStatus(parseInt(id, 10), 'paid');
    } catch {
      // Error handled by store
    }
  };

  const handleResend = async () => {
    if (!id) return;
    clearError();
    try {
      await sendInvoice(parseInt(id, 10));
    } catch {
      // Error handled by store
    }
  };

  const getStatusColor = (status: InvoiceStatus) => {
    switch (status) {
      case 'draft':
        return 'bg-gray-100 text-gray-700';
      case 'sent':
        return 'bg-blue-100 text-blue-700';
      case 'paid':
        return 'bg-green-100 text-green-700';
      default:
        return 'bg-gray-100 text-gray-700';
    }
  };

  const getTradeIcon = (trade: string) => {
    switch (trade) {
      case 'plumbing':
        return '🚿';
      case 'electrical':
        return '⚡';
      case 'hvac':
        return '❄️';
      default:
        return '🔧';
    }
  };

  if (isLoading && !currentInvoice) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-blue-600 border-t-transparent" />
      </div>
    );
  }

  if (!currentInvoice) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-500">Invoice not found</p>
          <button
            onClick={() => navigate('/invoices')}
            className="mt-4 text-blue-600 hover:text-blue-500"
          >
            Back to invoices
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-lg mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              onClick={() => navigate('/invoices')}
              className="p-2 -ml-2 text-gray-600 hover:bg-gray-100 rounded-full"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            <div>
              <h1 className="text-lg font-bold text-gray-900">Invoice #{currentInvoice.id}</h1>
              <p className="text-xs text-gray-500">{format.date(currentInvoice.created_at)}</p>
            </div>
          </div>
          <div className="relative">
            <button
              onClick={() => setShowActions(!showActions)}
              className="p-2 text-gray-600 hover:bg-gray-100 rounded-full"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z" />
              </svg>
            </button>
            {showActions && (
              <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-20">
                {currentInvoice.status === 'draft' && (
                  <button
                    onClick={() => {
                      setShowActions(false);
                      navigate(`/invoices/${id}/edit`);
                    }}
                    className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    Edit Invoice
                  </button>
                )}
                {currentInvoice.status !== 'paid' && (
                  <button
                    onClick={() => {
                      setShowActions(false);
                      handleMarkPaid();
                    }}
                    className="w-full text-left px-4 py-2 text-sm text-green-600 hover:bg-gray-100"
                  >
                    Mark as Paid
                  </button>
                )}
                {currentInvoice.status === 'sent' && (
                  <button
                    onClick={() => {
                      setShowActions(false);
                      handleResend();
                    }}
                    className="w-full text-left px-4 py-2 text-sm text-blue-600 hover:bg-gray-100"
                  >
                    Resend Invoice
                  </button>
                )}
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

        {/* Status Banner */}
        <div className={`mb-4 p-3 rounded-lg ${getStatusColor(currentInvoice.status)}`}>
          <div className="flex items-center justify-between">
            <span className="font-medium capitalize">{currentInvoice.status}</span>
            {currentInvoice.pdf_url && (
              <a
                href={currentInvoice.pdf_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm underline"
              >
                View PDF
              </a>
            )}
          </div>
        </div>

        {/* Trade Type */}
        <div className="bg-white rounded-lg border border-gray-200 p-4 mb-4">
          <div className="flex items-center gap-3">
            <span className="text-2xl">{getTradeIcon(currentInvoice.trade_type)}</span>
            <div>
              <p className="text-sm text-gray-500">Trade Type</p>
              <p className="font-medium capitalize">{currentInvoice.trade_type}</p>
            </div>
          </div>
        </div>

        {/* Client Info */}
        <div className="bg-white rounded-lg border border-gray-200 p-4 mb-4">
          <h2 className="font-semibold text-gray-900 mb-3">Client Information</h2>
          <div className="space-y-2">
            <div>
              <p className="text-sm text-gray-500">Name</p>
              <p className="font-medium">{currentInvoice.client_name}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Email</p>
              <p className="font-medium">{currentInvoice.client_email}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Job Address</p>
              <p className="font-medium">{currentInvoice.job_address}</p>
            </div>
          </div>
        </div>

        {/* Line Items */}
        <div className="bg-white rounded-lg border border-gray-200 p-4 mb-4">
          <h2 className="font-semibold text-gray-900 mb-3">Items</h2>
          <div className="space-y-3">
            {currentInvoice.line_items.map((item) => (
              <div key={item.id} className="flex justify-between items-start py-2 border-b border-gray-100 last:border-0">
                <div>
                  <p className="font-medium">{item.description}</p>
                  <p className="text-sm text-gray-500">
                    {format.number(item.quantity)} × {format.currency(item.unit_price)}
                  </p>
                </div>
                <span className="font-medium">{format.currency(item.line_total)}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Totals */}
        <div className="bg-gray-100 rounded-lg p-4 mb-4">
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Subtotal</span>
              <span className="font-medium">{format.currency(currentInvoice.totals.subtotal)}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Tax ({currentInvoice.tax_rate}%)</span>
              <span className="font-medium">{format.currency(currentInvoice.totals.tax_amount)}</span>
            </div>
            <div className="flex justify-between text-lg pt-2 border-t border-gray-300">
              <span className="font-semibold">Total</span>
              <span className="font-bold text-blue-600">{format.currency(currentInvoice.totals.total)}</span>
            </div>
          </div>
        </div>

        {/* Actions */}
        {currentInvoice.status === 'draft' && (
          <div className="space-y-3">
            <button
              onClick={() => navigate(`/invoices/${id}/edit`)}
              className="w-full py-3 px-4 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700"
            >
              Edit Invoice
            </button>
            <button
              onClick={handleResend}
              disabled={isLoading}
              className="w-full py-3 px-4 bg-green-600 text-white font-medium rounded-md hover:bg-green-700 disabled:opacity-50"
            >
              {isLoading ? 'Sending...' : 'Send to Client'}
            </button>
          </div>
        )}

        {currentInvoice.status === 'sent' && (
          <div className="space-y-3">
            <button
              onClick={handleMarkPaid}
              disabled={isLoading}
              className="w-full py-3 px-4 bg-green-600 text-white font-medium rounded-md hover:bg-green-700 disabled:opacity-50"
            >
              {isLoading ? 'Updating...' : 'Mark as Paid'}
            </button>
            <button
              onClick={handleResend}
              disabled={isLoading}
              className="w-full py-3 px-4 bg-white border-2 border-gray-300 text-gray-700 font-medium rounded-md hover:bg-gray-50 disabled:opacity-50"
            >
              {isLoading ? 'Sending...' : 'Resend Invoice'}
            </button>
          </div>
        )}
      </main>
    </div>
  );
}
