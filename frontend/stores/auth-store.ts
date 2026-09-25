import { create } from 'zustand';
import { createJSONStorage, persist } from 'zustand/middleware';
import { User } from '@/types/user';

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  hasHydrated: boolean;
  setHasHydrated: (hasHydrated: boolean) => void;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

interface LoginApiResponse {
  access_token: string;
  token_type: string;
  user: {
    id: string;
    email: string;
    name: string;
    role: User['role'];
  };
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:9000';
const AUTH_STORAGE_KEY = 'auth-session-storage';

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      hasHydrated: false,

      setHasHydrated: (hasHydrated: boolean) => {
        set({ hasHydrated });
      },

      login: async (email: string, password: string) => {
        const response = await fetch(`${API_URL}/api/v1/auth/login`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ email, password }),
        });

        const payload = (await response.json().catch(() => null)) as LoginApiResponse | { detail?: string } | null;

        if (!response.ok || !payload || !('access_token' in payload)) {
          const detail =
            payload && 'detail' in payload && typeof payload.detail === 'string'
              ? payload.detail
              : 'Invalid email or password';
          throw new Error(detail);
        }

        const now = new Date().toISOString();
        const user: User = {
          ...payload.user,
          avatar: undefined,
          createdAt: now,
          updatedAt: now,
        };

        set({ user, token: payload.access_token, isAuthenticated: true });
      },

      logout: () => {
        set({ user: null, token: null, isAuthenticated: false });
      },
    }),
    {
      name: AUTH_STORAGE_KEY,
      storage: createJSONStorage(() => sessionStorage),
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
      onRehydrateStorage: () => (state) => {
        state?.setHasHydrated(true);
      },
    }
  )
);
