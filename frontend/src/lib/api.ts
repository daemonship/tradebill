import axios, { AxiosError } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Types matching backend schemas
export interface User {
  id: number;
  email: string;
  created_at: string;
}

export interface BusinessProfile {
  id: number;
  user_id: number;
  business_name: string;
  phone?: string;
  email?: string;
  license_number?: string;
  created_at: string;
  updated_at?: string;
}

export type TradeType = 'plumbing' | 'electrical' | 'hvac';
export type InvoiceStatus = 'draft' | 'sent' | 'paid';
export type LineItemCategory = 'parts' | 'labor';

export interface LineItem {
  id: number;
  description: string;
  quantity: number;
  unit_price: number;
  category: LineItemCategory;
  line_total: number;
}

export interface LineItemSummary {
  category: string;
  total: number;
}

export interface InvoiceTotals {
  subtotal: number;
  tax_amount: number;
  total: number;
  category_breakdown: LineItemSummary[];
}

export interface Invoice {
  id: number;
  user_id: number;
  client_name: string;
  client_email: string;
  job_address: string;
  trade_type: TradeType;
  tax_rate: number;
  status: InvoiceStatus;
  pdf_url?: string;
  created_at: string;
  updated_at?: string;
  line_items: LineItem[];
  totals: InvoiceTotals;
}

export interface InvoiceListItem {
  id: number;
  client_name: string;
  job_address: string;
  trade_type: TradeType;
  status: InvoiceStatus;
  total: number;
  created_at: string;
}

// Auth API
export const authApi = {
  register: (email: string, password: string) =>
    api.post<User>('/auth/register', { email, password }),
  
  login: (email: string, password: string) =>
    api.post<{ access_token: string; token_type: string }>('/auth/login', 
      new URLSearchParams({ username: email, password }),
      { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } }
    ),
};

// Profile API
export const profileApi = {
  get: () => api.get<BusinessProfile>('/profile'),
  create: (data: Omit<BusinessProfile, 'id' | 'user_id' | 'created_at' | 'updated_at'>) =>
    api.post<BusinessProfile>('/profile', data),
  update: (data: Partial<Omit<BusinessProfile, 'id' | 'user_id' | 'created_at' | 'updated_at'>>) =>
    api.put<BusinessProfile>('/profile', data),
};

// Invoice API
export const invoiceApi = {
  list: () => api.get<InvoiceListItem[]>('/invoices'),
  get: (id: number) => api.get<Invoice>(`/invoices/${id}`),
  create: (data: {
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
  }) => api.post<Invoice>('/invoices', data),
  update: (id: number, data: {
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
  }) => api.put<Invoice>(`/invoices/${id}`, data),
  updateStatus: (id: number, status: InvoiceStatus) =>
    api.patch<Invoice>(`/invoices/${id}/status`, { status }),
  send: (id: number) => api.post<Invoice>(`/invoices/${id}/send`),
};
