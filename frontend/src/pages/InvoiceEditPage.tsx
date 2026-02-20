import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useInvoiceStore } from '../stores/invoiceStore';
import { TradeType, LineItemCategory, LineItem } from '../lib/api';
import { format } from '../lib/utils';

interface LineItemInput {
  id: string;
  description: string;
  quantity: string;
  unit_price: string;
  category: LineItemCategory;
}

const TRADE_TYPES: { value: TradeType; label: string; icon: string }[] = [
  { value: 'plumbing', label: 'Plumbing', icon: '🚿' },
  { value: 'electrical', label: 'Electrical', icon: '⚡' },
  { value: 'hvac', label: 'HVAC', icon: '❄️' },
];

const EMPTY_LINE_ITEM = (category: LineItemCategory): LineItemInput => ({
  id: Math.random().toString(36).substr(2, 9),
  description: '',
  quantity: '1',
  unit_price: '',
  category,
});

const lineItemToInput = (item: LineItem): LineItemInput => ({
  id: Math.random().toString(36).substr(2, 9),
  description: item.description,
  quantity: item.quantity.toString(),
  unit_price: item.unit_price.toString(),
  category: item.category,
});

export default function InvoiceEditPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { currentInvoice, fetchInvoice, updateInvoice, isLoading, error, clearError } = useInvoiceStore();

  const [tradeType, setTradeType] = useState<TradeType>('plumbing');
  const [clientName, setClientName] = useState('');
  const [clientEmail, setClientEmail] = useState('');
  const [jobAddress, setJobAddress] = useState('');
  const [taxRate, setTaxRate] = useState('8.25');
  const [parts, setParts] = useState<LineItemInput[]>([EMPTY_LINE_ITEM('parts')]);
  const [labor, setLabor] = useState<LineItemInput[]>([EMPTY_LINE_ITEM('labor')]);

  useEffect(() => {
    if (id) {
      fetchInvoice(parseInt(id, 10));
    }
  }, [id, fetchInvoice]);

  useEffect(() => {
    if (currentInvoice) {
      setTradeType(currentInvoice.trade_type);
      setClientName(currentInvoice.client_name);
      setClientEmail(currentInvoice.client_email);
      setJobAddress(currentInvoice.job_address);
      setTaxRate(currentInvoice.tax_rate.toString());
      
      const existingParts = currentInvoice.line_items
        .filter((item) => item.category === 'parts')
        .map(lineItemToInput);
      const existingLabor = currentInvoice.line_items
        .filter((item) => item.category === 'labor')
        .map(lineItemToInput);
      
      setParts(existingParts.length > 0 ? existingParts : [EMPTY_LINE_ITEM('parts')]);
      setLabor(existingLabor.length > 0 ? existingLabor : [EMPTY_LINE_ITEM('labor')]);
    }
  }, [currentInvoice]);

  const calculateTotals = () => {
    const allItems = [...parts, ...labor];
    const subtotal = allItems.reduce((sum, item) => {
      const qty = parseFloat(item.quantity) || 0;
      const price = parseFloat(item.unit_price) || 0;
      return sum + qty * price;
    }, 0);
    const taxRateNum = parseFloat(taxRate) || 0;
    const taxAmount = subtotal * (taxRateNum / 100);
    const total = subtotal + taxAmount;
    return { subtotal, taxAmount, total };
  };

  const { subtotal, taxAmount, total } = calculateTotals();

  const updateLineItem = (
    items: LineItemInput[],
    setItems: (items: LineItemInput[]) => void,
    itemId: string,
    field: keyof LineItemInput,
    value: string
  ) => {
    setItems(
      items.map((item) => (item.id === itemId ? { ...item, [field]: value } : item))
    );
  };

  const addLineItem = (category: LineItemCategory) => {
    if (category === 'parts') {
      setParts([...parts, EMPTY_LINE_ITEM('parts')]);
    } else {
      setLabor([...labor, EMPTY_LINE_ITEM('labor')]);
    }
  };

  const removeLineItem = (category: LineItemCategory, itemId: string) => {
    if (category === 'parts') {
      setParts(parts.filter((p) => p.id !== itemId));
    } else {
      setLabor(labor.filter((l) => l.id !== itemId));
    }
  };

  const handleSave = async () => {
    if (!id) return;
    clearError();

    const validParts = parts.filter(
      (p) => p.description.trim() && parseFloat(p.unit_price) > 0
    );
    const validLabor = labor.filter(
      (l) => l.description.trim() && parseFloat(l.unit_price) > 0
    );

    const lineItems = [...validParts, ...validLabor].map((item) => ({
      description: item.description,
      quantity: parseFloat(item.quantity) || 1,
      unit_price: parseFloat(item.unit_price),
      category: item.category,
    }));

    try {
      await updateInvoice(parseInt(id, 10), {
        client_name: clientName,
        client_email: clientEmail,
        job_address: jobAddress,
        trade_type: tradeType,
        tax_rate: parseFloat(taxRate) || 0,
        line_items: lineItems,
      });
      navigate(`/invoices/${id}`);
    } catch {
      // Error handled by store
    }
  };

  if (!currentInvoice && !isLoading) {
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
        <div className="max-w-lg mx-auto px-4 py-3 flex items-center gap-3">
          <button
            onClick={() => navigate(`/invoices/${id}`)}
            className="p-2 -ml-2 text-gray-600 hover:bg-gray-100 rounded-full"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <h1 className="text-lg font-bold text-gray-900">Edit Invoice</h1>
        </div>
      </header>

      {/* Content */}
      <main className="max-w-lg mx-auto px-4 py-4">
        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
            <p className="text-sm text-red-700">{error}</p>
          </div>
        )}

        {/* Trade Type */}
        <div className="bg-white rounded-lg border border-gray-200 p-4 mb-4">
          <h2 className="font-semibold text-gray-900 mb-3">Trade Type</h2>
          <div className="space-y-2">
            {TRADE_TYPES.map((trade) => (
              <button
                key={trade.value}
                onClick={() => setTradeType(trade.value)}
                className={`w-full p-3 rounded-lg border-2 text-left flex items-center gap-3 transition-colors ${
                  tradeType === trade.value
                    ? 'border-blue-600 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <span className="text-xl">{trade.icon}</span>
                <span className="font-medium">{trade.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Client Info */}
        <div className="bg-white rounded-lg border border-gray-200 p-4 mb-4">
          <h2 className="font-semibold text-gray-900 mb-3">Client Information</h2>
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Client Name *
              </label>
              <input
                type="text"
                value={clientName}
                onChange={(e) => setClientName(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="John Smith"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Client Email *
              </label>
              <input
                type="email"
                value={clientEmail}
                onChange={(e) => setClientEmail(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="john@example.com"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Job Address *
              </label>
              <textarea
                value={jobAddress}
                onChange={(e) => setJobAddress(e.target.value)}
                rows={2}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="123 Main St, City, State 12345"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Tax Rate (%)
              </label>
              <input
                type="number"
                value={taxRate}
                onChange={(e) => setTaxRate(e.target.value)}
                step="0.01"
                min="0"
                max="100"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>

        {/* Parts Section */}
        <div className="bg-white rounded-lg border border-gray-200 p-4 mb-4">
          <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
            <span>🔧</span> Parts
          </h3>
          <div className="space-y-3">
            {parts.map((part) => (
              <div key={part.id} className="space-y-2 p-2 bg-gray-50 rounded">
                <input
                  type="text"
                  value={part.description}
                  onChange={(e) =>
                    updateLineItem(parts, setParts, part.id, 'description', e.target.value)
                  }
                  placeholder="Part description"
                  className="w-full px-2 py-1.5 text-sm border border-gray-300 rounded"
                />
                <div className="flex gap-2">
                  <input
                    type="number"
                    value={part.quantity}
                    onChange={(e) =>
                      updateLineItem(parts, setParts, part.id, 'quantity', e.target.value)
                    }
                    placeholder="Qty"
                    min="0"
                    step="0.01"
                    className="w-20 px-2 py-1.5 text-sm border border-gray-300 rounded"
                  />
                  <input
                    type="number"
                    value={part.unit_price}
                    onChange={(e) =>
                      updateLineItem(parts, setParts, part.id, 'unit_price', e.target.value)
                    }
                    placeholder="Price $"
                    min="0"
                    step="0.01"
                    className="flex-1 px-2 py-1.5 text-sm border border-gray-300 rounded"
                  />
                  {parts.length > 1 && (
                    <button
                      onClick={() => removeLineItem('parts', part.id)}
                      className="p-1.5 text-red-600 hover:bg-red-50 rounded"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
          <button
            onClick={() => addLineItem('parts')}
            className="mt-3 w-full py-2 text-sm text-blue-600 border border-dashed border-blue-300 rounded hover:bg-blue-50"
          >
            + Add Part
          </button>
        </div>

        {/* Labor Section */}
        <div className="bg-white rounded-lg border border-gray-200 p-4 mb-4">
          <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
            <span>👷</span> Labor
          </h3>
          <div className="space-y-3">
            {labor.map((item) => (
              <div key={item.id} className="space-y-2 p-2 bg-gray-50 rounded">
                <input
                  type="text"
                  value={item.description}
                  onChange={(e) =>
                    updateLineItem(labor, setLabor, item.id, 'description', e.target.value)
                  }
                  placeholder="Labor description"
                  className="w-full px-2 py-1.5 text-sm border border-gray-300 rounded"
                />
                <div className="flex gap-2">
                  <input
                    type="number"
                    value={item.quantity}
                    onChange={(e) =>
                      updateLineItem(labor, setLabor, item.id, 'quantity', e.target.value)
                    }
                    placeholder="Hours"
                    min="0"
                    step="0.25"
                    className="w-20 px-2 py-1.5 text-sm border border-gray-300 rounded"
                  />
                  <input
                    type="number"
                    value={item.unit_price}
                    onChange={(e) =>
                      updateLineItem(labor, setLabor, item.id, 'unit_price', e.target.value)
                    }
                    placeholder="Rate $/hr"
                    min="0"
                    step="0.01"
                    className="flex-1 px-2 py-1.5 text-sm border border-gray-300 rounded"
                  />
                  {labor.length > 1 && (
                    <button
                      onClick={() => removeLineItem('labor', item.id)}
                      className="p-1.5 text-red-600 hover:bg-red-50 rounded"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
          <button
            onClick={() => addLineItem('labor')}
            className="mt-3 w-full py-2 text-sm text-blue-600 border border-dashed border-blue-300 rounded hover:bg-blue-50"
          >
            + Add Labor
          </button>
        </div>

        {/* Totals */}
        <div className="bg-gray-100 rounded-lg p-4 mb-4">
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Subtotal</span>
              <span className="font-medium">{format.currency(subtotal)}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Tax ({taxRate}%)</span>
              <span className="font-medium">{format.currency(taxAmount)}</span>
            </div>
            <div className="flex justify-between text-lg pt-2 border-t border-gray-300">
              <span className="font-semibold">Total</span>
              <span className="font-bold text-blue-600">{format.currency(total)}</span>
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-3">
          <button
            onClick={() => navigate(`/invoices/${id}`)}
            className="flex-1 py-3 px-4 bg-gray-200 text-gray-700 font-medium rounded-md hover:bg-gray-300"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            disabled={isLoading || total <= 0}
            className="flex-1 py-3 px-4 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 disabled:opacity-50"
          >
            {isLoading ? 'Saving...' : 'Save Changes'}
          </button>
        </div>
      </main>
    </div>
  );
}
