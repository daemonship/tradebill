import { create } from 'zustand';
import { invoiceApi, Invoice, InvoiceListItem, InvoiceStatus, TradeType, LineItemCategory } from '../lib/api';

interface InvoiceState {
  invoices: InvoiceListItem[];
  currentInvoice: Invoice | null;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  fetchInvoices: () => Promise<void>;
  fetchInvoice: (id: number) => Promise<void>;
  createInvoice: (data: {
    client_name: string;
    client_email: string;
    job_address: string;
    trade_type: TradeType;
    tax_rate: number;
    line_items: Array<{
      description: string;
      quantity: number;
      unit_price: number;
      category: LineItemCategory;
    }>;
  }) => Promise<Invoice>;
  updateInvoice: (id: number, data: {
    client_name: string;
    client_email: string;
    job_address: string;
    trade_type: TradeType;
    tax_rate: number;
    line_items: Array<{
      description: string;
      quantity: number;
      unit_price: number;
      category: LineItemCategory;
    }>;
  }) => Promise<Invoice>;
  updateStatus: (id: number, status: InvoiceStatus) => Promise<void>;
  sendInvoice: (id: number) => Promise<void>;
  clearError: () => void;
  clearCurrentInvoice: () => void;
}

export const useInvoiceStore = create<InvoiceState>((set) => ({
  invoices: [],
  currentInvoice: null,
  isLoading: false,
  error: null,

  fetchInvoices: async () => {
    set({ isLoading: true, error: null });
    try {
      const response = await invoiceApi.list();
      set({ invoices: response.data, isLoading: false });
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : 'Failed to fetch invoices';
      set({ error: message, isLoading: false });
      throw error;
    }
  },

  fetchInvoice: async (id) => {
    set({ isLoading: true, error: null });
    try {
      const response = await invoiceApi.get(id);
      set({ currentInvoice: response.data, isLoading: false });
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : 'Failed to fetch invoice';
      set({ error: message, isLoading: false });
      throw error;
    }
  },

  createInvoice: async (data) => {
    set({ isLoading: true, error: null });
    try {
      const response = await invoiceApi.create(data);
      const newInvoice = response.data;
      set((state) => ({
        invoices: [{
          id: newInvoice.id,
          client_name: newInvoice.client_name,
          job_address: newInvoice.job_address,
          trade_type: newInvoice.trade_type,
          status: newInvoice.status,
          total: newInvoice.totals.total,
          created_at: newInvoice.created_at,
        }, ...state.invoices],
        currentInvoice: newInvoice,
        isLoading: false,
      }));
      return newInvoice;
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : 'Failed to create invoice';
      set({ error: message, isLoading: false });
      throw error;
    }
  },

  updateInvoice: async (id, data) => {
    set({ isLoading: true, error: null });
    try {
      const response = await invoiceApi.update(id, data);
      const updatedInvoice = response.data;
      set((state) => ({
        invoices: state.invoices.map((inv) =>
          inv.id === id
            ? {
                ...inv,
                client_name: updatedInvoice.client_name,
                job_address: updatedInvoice.job_address,
                trade_type: updatedInvoice.trade_type,
                status: updatedInvoice.status,
                total: updatedInvoice.totals.total,
              }
            : inv
        ),
        currentInvoice: updatedInvoice,
        isLoading: false,
      }));
      return updatedInvoice;
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : 'Failed to update invoice';
      set({ error: message, isLoading: false });
      throw error;
    }
  },

  updateStatus: async (id, status) => {
    set({ isLoading: true, error: null });
    try {
      const response = await invoiceApi.updateStatus(id, status);
      const updatedInvoice = response.data;
      set((state) => ({
        invoices: state.invoices.map((inv) =>
          inv.id === id ? { ...inv, status: updatedInvoice.status } : inv
        ),
        currentInvoice: updatedInvoice,
        isLoading: false,
      }));
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : 'Failed to update status';
      set({ error: message, isLoading: false });
      throw error;
    }
  },

  sendInvoice: async (id) => {
    set({ isLoading: true, error: null });
    try {
      const response = await invoiceApi.send(id);
      const updatedInvoice = response.data;
      set((state) => ({
        invoices: state.invoices.map((inv) =>
          inv.id === id
            ? { ...inv, status: updatedInvoice.status, total: updatedInvoice.totals.total }
            : inv
        ),
        currentInvoice: updatedInvoice,
        isLoading: false,
      }));
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : 'Failed to send invoice';
      set({ error: message, isLoading: false });
      throw error;
    }
  },

  clearError: () => set({ error: null }),
  clearCurrentInvoice: () => set({ currentInvoice: null }),
}));
