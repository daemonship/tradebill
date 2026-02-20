import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { authApi, profileApi, User, BusinessProfile } from '../lib/api';

interface AuthState {
  token: string | null;
  user: User | null;
  profile: BusinessProfile | null;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  setToken: (token: string | null) => void;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => void;
  fetchProfile: () => Promise<void>;
  createProfile: (data: Omit<BusinessProfile, 'id' | 'user_id' | 'created_at' | 'updated_at'>) => Promise<void>;
  updateProfile: (data: Partial<Omit<BusinessProfile, 'id' | 'user_id' | 'created_at' | 'updated_at'>>) => Promise<void>;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      token: null,
      user: null,
      profile: null,
      isLoading: false,
      error: null,

      setToken: (token) => {
        set({ token });
        if (token) {
          localStorage.setItem('token', token);
        } else {
          localStorage.removeItem('token');
        }
      },

      login: async (email, password) => {
        set({ isLoading: true, error: null });
        try {
          const response = await authApi.login(email, password);
          const { access_token } = response.data;
          localStorage.setItem('token', access_token);
          set({ token: access_token, isLoading: false });
          
          // Try to fetch profile after login
          try {
            await get().fetchProfile();
          } catch {
            // Profile might not exist yet, that's ok
            set({ profile: null });
          }
        } catch (error: unknown) {
          const message = error instanceof Error ? error.message : 'Login failed';
          set({ error: message, isLoading: false });
          throw error;
        }
      },

      register: async (email, password) => {
        set({ isLoading: true, error: null });
        try {
          await authApi.register(email, password);
          // Auto-login after registration
          await get().login(email, password);
        } catch (error: unknown) {
          const message = error instanceof Error ? error.message : 'Registration failed';
          set({ error: message, isLoading: false });
          throw error;
        }
      },

      logout: () => {
        localStorage.removeItem('token');
        set({ token: null, user: null, profile: null, error: null });
      },

      fetchProfile: async () => {
        try {
          const response = await profileApi.get();
          set({ profile: response.data });
        } catch (error) {
          set({ profile: null });
          throw error;
        }
      },

      createProfile: async (data) => {
        set({ isLoading: true, error: null });
        try {
          const response = await profileApi.create(data);
          set({ profile: response.data, isLoading: false });
        } catch (error: unknown) {
          const message = error instanceof Error ? error.message : 'Failed to create profile';
          set({ error: message, isLoading: false });
          throw error;
        }
      },

      updateProfile: async (data) => {
        set({ isLoading: true, error: null });
        try {
          const response = await profileApi.update(data);
          set({ profile: response.data, isLoading: false });
        } catch (error: unknown) {
          const message = error instanceof Error ? error.message : 'Failed to update profile';
          set({ error: message, isLoading: false });
          throw error;
        }
      },

      clearError: () => set({ error: null }),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ token: state.token }),
    }
  )
);
